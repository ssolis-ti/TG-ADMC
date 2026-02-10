from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel

from src.db.database import get_session
from src.services.marketplace import MarketplaceService
from src.services.escrow import EscrowService
from src.services.identity import IdentityService
from src.db.models import Channel, Deal, User
from src.utils.auth import get_current_user # [SECURITY] Import Dependency

router = APIRouter(prefix="/api", tags=["Marketplace"])

# --- Schemas (Data Validation) ---
class ChannelResponse(BaseModel):
    """
    [DTO]: Enhanced Channel Public View
    Includes verified metrics for high-trust marketplace.
    """
    id: int
    title: str
    username: Optional[str]
    subscribers: int
    avg_views: int
    language: str
    premium_ratio: float
    price_post: float
    verified: bool

class CreateDealRequest(BaseModel):
    """
    DTO for Deal Creation.
    """
    # TODO: [Security] In production, extract this from JWT/InitData.
    # We pass it explicitly here only for MVP simulation.
    advertiser_id: int 
    channel_id: int
    brief: str
    amount: float

class ActionWithContent(BaseModel):
    """ Generic DTO for actions that require text (Draft, Revision) """
    user_id: int
    content: str

class ActionSimple(BaseModel):
    """ DTO for actions that only need user_id """
    user_id: int

class PaymentConfirmation(BaseModel):
    """ [STEP 5] DTO for locking funds after TON Connect Tx """
    user_id: int
    transaction_hash: str

class UpdateChannelRequest(BaseModel):
    """
    DTO for updating channel settings (Price).
    """
    user_id: int
    price_post: float

class WalletUpdateRequest(BaseModel):
    """
    [ESCROW FIX] DTO for saving user's wallet address.
    Called when user connects their TON wallet.
    """
    user_id: int
    wallet_address: str

class RoleUpdateRequest(BaseModel):
    """
    [ROLE FIX] DTO for saving user's role when they select a path.
    """
    user_id: int
    role: str  # 'advertiser' or 'owner'

# --- Endpoints ---

@router.get("/channels", response_model=List[ChannelResponse])
async def get_channels(
    limit: int = 20, 
    offset: int = 0, 
    session: AsyncSession = Depends(get_session)
    # user: dict = Depends(get_current_user) # [SECURITY]: Descomentar para activar "Auth Shield"
):
    """
    [TACTICAL PURPOSE]: Public Marketplace Feed.
    [DATA FLOW]: Fetch Verified Channels -> Filter by Metrics -> Serve to Advertiser UI.
    Using 'limit/offset' for Infinite Scroll efficiency.
    """
    service = MarketplaceService(session)
    channels = await service.list_verified_channels(limit, offset)
    return channels

@router.get("/channels/user/{user_id}", response_model=List[ChannelResponse])
async def get_user_channels(
    user_id: int,
    session: AsyncSession = Depends(get_session)
):
    """
    [OWNER DASHBOARD]: Get simplified list of My Channels.
    """
    ident_service = IdentityService(session)
    # Map TG ID to DB ID
    user = await ident_service.get_or_create_user(user_id)
    
    from sqlmodel import select
    from src.db.models import Channel
    stmt = select(Channel).where(Channel.owner_id == user.id)
    result = await session.exec(stmt)
    stmt = select(Channel).where(Channel.owner_id == user.id)
    result = await session.exec(stmt)
    return result.all()

@router.post("/user/wallet")
async def update_user_wallet(
    req: WalletUpdateRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    [ESCROW FIX]: Save user's wallet address when they connect via TON Connect.
    This is CRITICAL for the payout system to work.
    """
    ident_service = IdentityService(session)
    user = await ident_service.get_or_create_user(req.user_id)
    
    # Update wallet address
    user.wallet_address = req.wallet_address
    session.add(user)
    await session.commit()
    
    return {"status": "updated", "wallet_address": req.wallet_address}

@router.post("/user/role")
async def update_user_role(
    req: RoleUpdateRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    [ROLE FIX]: Save user's role when they select Advertiser/Owner path.
    This is CRITICAL for correct deal flow.
    """
    from src.db.models import UserRole
    
    ident_service = IdentityService(session)
    user = await ident_service.get_or_create_user(req.user_id)
    
    # Map string to enum
    role_map = {
        'advertiser': UserRole.ADVERTISER,
        'owner': UserRole.OWNER
    }
    
    if req.role.lower() in role_map:
        user.role = role_map[req.role.lower()]
        session.add(user)
        await session.commit()
        return {"status": "updated", "role": user.role.value}
    else:
        raise HTTPException(status_code=400, detail=f"Invalid role: {req.role}")

@router.put("/channels/{channel_id}")
async def update_channel_price(
    channel_id: int,
    req: UpdateChannelRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    [OWNER]: Update Channel Price.
    """
    ident_service = IdentityService(session)
    user = await ident_service.get_or_create_user(req.user_id)
    
    # Verify Ownership
    channel = await session.get(Channel, channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    if channel.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    await ident_service.set_channel_price(channel.id, req.price_post)
    return {"status": "updated", "new_price": req.price_post}

@router.post("/deals/create")
async def create_deal(
    request: CreateDealRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    [GENESIS]: Initiates the Deal Organism.
    [INFECTION PATH]: Frontend Form -> API -> DB (Status: CREATED).
    Triggers notification to Channel Owner via Bot (Viral Spread).
    """
    ident_service = IdentityService(session)
    escrow_service = EscrowService(session)
    try:
        # [MAPPING]: Linking Telegram User -> Internal Host ID
        advertiser = await ident_service.get_or_create_user(request.advertiser_id)
        
        deal = await escrow_service.create_deal_request(
            advertiser_id=advertiser.id, # Internal DB ID
            channel_id=request.channel_id, # Targeted Channel Node
            brief=request.brief,
            amount=request.amount
        )
        return {"status": "created", "deal_id": deal.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/deals/{deal_id}")
async def get_deal(deal_id: int, session: AsyncSession = Depends(get_session)):
    """
    Get Deal status/details.
    """
    deal = await session.get(Deal, deal_id)
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    return deal

@router.post("/deals/{deal_id}/accept")
async def accept_deal(
    deal_id: int, 
    req: ActionSimple,  # [FIX]: Changed from ActionWithContent
    session: AsyncSession = Depends(get_session)
):
    """
    [Channel Owner] Accept a deal proposal.
    """
    ident_service = IdentityService(session)
    escrow_service = EscrowService(session)
    try:
        user = await ident_service.get_or_create_user(req.user_id)
        deal = await escrow_service.accept_deal(deal_id, user.id)
        return {"status": deal.status}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/deals/{deal_id}/reject")
async def reject_deal(
    deal_id: int, 
    req: ActionWithContent,
    session: AsyncSession = Depends(get_session)
):
    """
    [Channel Owner] Reject a deal proposal.
    """
    ident_service = IdentityService(session)
    escrow_service = EscrowService(session)
    try:
        user = await ident_service.get_or_create_user(req.user_id)
        # Verify ownership (implicit in logic but good to enforce if needed, 
        # but Service handles status check which is primary guard)
        
        deal = await escrow_service.reject_deal(deal_id, req.content)
        return {"status": deal.status}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/deals/{deal_id}/submit-draft")
async def submit_draft(deal_id: int, req: ActionWithContent, session: AsyncSession = Depends(get_session)):
    """ [OWNER] Submit the creative draft """
    ident_service = IdentityService(session)
    escrow_service = EscrowService(session)
    try:
        user = await ident_service.get_or_create_user(req.user_id)
        deal = await escrow_service.submit_draft(deal_id, req.content)
        return {"status": deal.status}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/deals/{deal_id}/approve")
async def approve_deal(deal_id: int, req: ActionSimple, session: AsyncSession = Depends(get_session)):
    """ [ADVERTISER] Approve the draft """
    ident_service = IdentityService(session)
    escrow_service = EscrowService(session)
    try:
        user = await ident_service.get_or_create_user(req.user_id)
        deal = await session.get(Deal, deal_id)
        
        # [SECURITY]: Verify caller is the Advertiser
        if deal.advertiser_id != user.id:
            raise HTTPException(status_code=403, detail="Only the Advertiser can approve.")
        
        deal = await escrow_service.approve_draft(deal_id)
        return {"status": deal.status}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/deals/{deal_id}/request-revision")
async def request_revision(deal_id: int, req: ActionWithContent, session: AsyncSession = Depends(get_session)):
    """ [ADVERTISER] Ask for changes """
    ident_service = IdentityService(session)
    escrow_service = EscrowService(session)
    try:
        user = await ident_service.get_or_create_user(req.user_id)
        deal = await escrow_service.request_revision(deal_id, req.content)
        return {"status": deal.status}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

class DisputeRequest(BaseModel):
    """
    [HARDENING] DTO for raising a dispute on a deal.
    Available to both Advertiser and Owner roles.
    """
    user_id: int
    reason: str

@router.post("/deals/{deal_id}/confirm-payment")
async def confirm_payment(deal_id: int, req: PaymentConfirmation, session: AsyncSession = Depends(get_session)):
    """ [ADVERTISER] Confirm payment via TON Connect """
    ident_service = IdentityService(session)
    escrow_service = EscrowService(session)
    try:
        user = await ident_service.get_or_create_user(req.user_id)
        
        # [CRITICAL VULNERABILITY]: MVP Mode (Blind Trust).
        # [RAPAZ AUDIT REQUIRED]: En V2, esto DEBE conectarse a Toncenter API.
        # Check list:
        # 1. ¿El receptor es nuestra wallet?
        # 2. ¿El monto coincide con deal.amount?
        # 3. ¿El comentario es el deal.id?
        # Si falla -> RECHAZAR.
        deal = await escrow_service.lock_funds(deal_id, req.transaction_hash)
        return {"status": deal.status}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/deals/{deal_id}/dispute")
async def dispute_deal(
    deal_id: int,
    req: DisputeRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    [HARDENING] Raise a dispute on a deal.
    
    Available to both Advertiser and Owner.
    Flags the deal as disputed and logs the reason for admin review.
    Does NOT change deal status — just marks it for attention.
    """
    ident_service = IdentityService(session)
    escrow_service = EscrowService(session)
    try:
        user = await ident_service.get_or_create_user(req.user_id)
        deal = await escrow_service.raise_dispute(deal_id, req.reason)
        return {
            "status": "disputed",
            "deal_id": deal.id,
            "is_disputed": deal.is_disputed,
            "reason": deal.dispute_reason
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
@router.get("/deals/user/{user_id}")
async def get_user_deals(
    user_id: int, 
    session: AsyncSession = Depends(get_session)
):
    """
    [MVP REQ]: CRM Lite View
    Retrieves all deals relevant to the user (as Advertiser or Channel Manager).
    """
    from sqlmodel import select, or_
    from src.db.models import Channel, User
    
    # 1. Map telegram_id to DB user_id
    user_stmt = select(User.id).where(User.telegram_id == user_id)
    user_db_id = (await session.exec(user_stmt)).first()
    
    if not user_db_id:
        return []

    # 2. Fetch deals
    stmt = select(Deal).where(
        or_(
            Deal.advertiser_id == user_db_id,
            Deal.channel_id.in_(
                select(Channel.id).where(Channel.owner_id == user_db_id)
            )
        )
    )
    result = await session.exec(stmt)
    deals = result.all()
    
    # 3. Enrich with Role for Frontend Discrimination
    enriched_deals = []
    for deal in deals:
        role = "advertiser" if deal.advertiser_id == user_db_id else "owner"
        # Convert to dict and add role
        d = deal.model_dump()
        d["user_role"] = role
        enriched_deals.append(d)

    return enriched_deals
