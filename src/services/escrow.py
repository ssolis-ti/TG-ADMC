from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import Optional

from src.db.models import Deal, DealStatus, User
from src.core.logger import app_logger

class EscrowService:
    """
    [CORE ENGINE]: La Máquina de Estados (Escrow).
    [RESPONSIBILITY]: Gestionar la vida del contrato desde 'Created' hasta 'Completed'.
    [LOGIC]: 
    1. No toca Telegram (Agnóstico).
    2. Solo mueve estados si las condiciones previas se cumplen.
    
    Flow:
    CREATED -> ACCEPTED -> LOCKED (Funds Safe) -> SCHEDULED -> PUBLISHED -> COMPLETED
                                                                              |
    Any state can be flagged with is_disputed=True via raise_dispute()     [DISPUTED]
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.logger = app_logger

    async def reject_deal(self, deal_id: int, reason: str) -> Deal:
        """
        [STEP 2 Alt] Reject Deal
        ------------------------
        Owner rejects the deal.
        """
        deal = await self.session.get(Deal, deal_id)
        if not deal:
            raise ValueError("Deal not found")
            
        # Allow rejection if Created or Locked (Pre-Paid)
        if deal.status not in [DealStatus.CREATED, DealStatus.LOCKED]:
             raise ValueError("Cannot reject deal in current status")

        deal.status = DealStatus.REJECTED
        deal.rejection_reason = reason
        deal.updated_at = datetime.utcnow()
        await self.session.commit()
        
        self.logger.info(f"Deal Rejected: ID={deal.id} | Reason={reason}", extra={"deal_id": deal.id, "status": "REJECTED"})
        return deal

    async def create_deal_request(self, advertiser_id: int, channel_id: int, brief: str, amount: float) -> Deal:
        """
        [STEP 1] Create Deal Request
        ----------------------------
        Advertiser initiates by sending a brief.
        """
        deal = Deal(
            advertiser_id=advertiser_id,
            channel_id=channel_id,
            ad_brief=brief,
            amount_ton=amount,
            status=DealStatus.CREATED
        )
        self.session.add(deal)
        await self.session.commit()
        await self.session.refresh(deal)
        
        self.logger.info(f"Deal Created: ID={deal.id} | Advertiser={advertiser_id} | Channel={channel_id}", 
                         extra={"deal_id": deal.id, "action": "create_deal"})
        return deal

    async def accept_deal(self, deal_id: int, owner_id: int) -> Deal:
        """
        [STEP 2] Accept Deal (Smart Flow)
        ---------------------------------
        Owner accepts the deal.
        Logic branches based on payment status:
        A) Pre-Paid (LOCKED): Auto-Schedule immediately.
        B) Post-Paid (CREATED): Fast-track to Payment.
        """
        deal = await self.session.get(Deal, deal_id)
        if not deal:
            raise ValueError("Deal not found")
            
        # [AUTO-FILL]: Assume Advertiser sent final content in brief
        deal.ad_draft = deal.ad_brief
        deal.updated_at = datetime.utcnow()

        if deal.status == DealStatus.LOCKED:
            # [SCENARIO A]: Pre-Paid. Launch immediately!
            deal.status = DealStatus.SCHEDULED
            deal.scheduled_at = datetime.utcnow()
            self.logger.info(f"Pre-Paid Deal Accepted & Auto-Launched: ID={deal.id}", extra={"deal_id": deal.id, "status": "SCHEDULED"})
        else:
             # [SCENARIO B]: Post-Paid. Fast-track to Payment.
            deal.status = DealStatus.AWAITING_PAYMENT
            self.logger.info(f"Deal Accepted & Waiting Payment: ID={deal.id}", extra={"deal_id": deal.id, "status": "AWAITING_PAYMENT"})
        
        await self.session.commit()
        return deal

    async def submit_draft(self, deal_id: int, content: str) -> Deal:
        """
        [STEP 3] Submit Draft
        ---------------------
        Owner submits the actual ad content (text/media) for review.
        """
        deal = await self.session.get(Deal, deal_id)
        if deal.status not in [DealStatus.ACCEPTED, DealStatus.REVISION_REQUESTED]:
            raise ValueError("Invalid status for draft submission")
            
        deal.ad_draft = content
        deal.status = DealStatus.DRAFT_SUBMITTED
        deal.updated_at = datetime.utcnow()
        await self.session.commit()
        
        self.logger.info(f"Draft Submitted: ID={deal.id}", extra={"deal_id": deal.id, "status": "DRAFTED"})
        return deal

    async def approve_draft(self, deal_id: int) -> Deal:
        """
        [STEP 4] Approve Draft
        ----------------------
        Advertiser likes the draft. Now moves to AWAITING_PAYMENT.
        """
        deal = await self.session.get(Deal, deal_id)
        if deal.status != DealStatus.DRAFT_SUBMITTED:
            raise ValueError("Nothing to approve")
            
        deal.status = DealStatus.AWAITING_PAYMENT
        deal.updated_at = datetime.utcnow()
        await self.session.commit()
        
        self.logger.info(f"Draft Approved: ID={deal.id}", extra={"deal_id": deal.id, "status": "AWAITING"})
        return deal

    async def request_revision(self, deal_id: int, reason: str) -> Deal:
        """
        [STEP 4 Alt] Request Revision
        ------------------------------
        Advertiser wants changes to the submitted draft.
        """
        deal = await self.session.get(Deal, deal_id)
        if not deal:
            raise ValueError("Deal not found")
        deal.rejection_reason = reason
        deal.status = DealStatus.REVISION_REQUESTED
        deal.updated_at = datetime.utcnow()
        await self.session.commit()
        
        self.logger.info(f"Revision Requested: ID={deal.id}", extra={"deal_id": deal.id, "status": "REVISION"})
        return deal

    async def lock_funds(self, deal_id: int, transaction_hash: str) -> Deal:
        """
        [STEP 3] Lock Funds (Escrow)
        """
        deal = await self.session.get(Deal, deal_id)
        
        # [FIX]: Support Pre-Paid Flow (allow locking from CREATED)
        valid_statuses = [DealStatus.AWAITING_PAYMENT, DealStatus.CREATED]
        if not deal or deal.status not in valid_statuses:
             raise ValueError(f"Deal status {deal.status} not valid for locking funds.")

        deal.payment_tx_hash = transaction_hash
        
        if deal.status == DealStatus.AWAITING_PAYMENT:
            # If it was waiting, now we auto-schedule (Post-Paid Flow complete)
            deal.status = DealStatus.SCHEDULED
            deal.scheduled_at = datetime.utcnow()
        else:
            # If it was CREATED (Pre-Paid), we just mark it LOCKED and wait for Owner Accept
            deal.status = DealStatus.LOCKED
            
        await self.session.commit()
        self.logger.info(f"Funds Locked: ID={deal.id} | Status={deal.status}", extra={"deal_id": deal.id, "status": deal.status.value})
        return deal
    
    async def schedule_post(self, deal_id: int, schedule_time: datetime) -> Deal:
        """
        Step 4: Post is scheduled for auto-posting.
        """
        deal = await self.session.get(Deal, deal_id)
        if deal.status != DealStatus.LOCKED:
             raise ValueError("Funds must be LOCKED before scheduling.")
        
        deal.scheduled_at = schedule_time
        deal.status = DealStatus.SCHEDULED
        await self.session.commit()
        
        self.logger.info(f"Post Scheduled: ID={deal.id} | Time={schedule_time}", extra={"deal_id": deal.id, "status": "SCHEDULED"})
        return deal

    async def complete_deal(self, deal_id: int) -> Deal:
        """
        Step Final: Verification successful, funds released.
        """
        deal = await self.session.get(Deal, deal_id)
        deal.status = DealStatus.COMPLETED
        deal.updated_at = datetime.utcnow()
        
        await self.session.commit()
        self.logger.info(f"Deal Completed: ID={deal.id} | Funds Released", extra={"deal_id": deal.id, "status": "COMPLETED"})
        return deal

    async def raise_dispute(self, deal_id: int, reason: str) -> Deal:
        """
        [HARDENING] Raise Dispute
        -------------------------
        Flags a deal as disputed. Does NOT change the deal status.
        This is an orthogonal flag: any deal in any state can be disputed.
        
        The dispute is logged at WARNING level for admin visibility.
        In production: this would trigger an admin notification (email/Telegram).
        """
        deal = await self.session.get(Deal, deal_id)
        if not deal:
            raise ValueError("Deal not found")
            
        deal.is_disputed = True
        deal.dispute_reason = reason
        deal.updated_at = datetime.utcnow()
        await self.session.commit()
        
        self.logger.warning(
            f"🚨 DISPUTE RAISED: Deal ID={deal.id} | Reason={reason}",
            extra={"deal_id": deal.id, "status": "DISPUTED"}
        )
        return deal
