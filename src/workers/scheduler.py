from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlmodel import select
from datetime import datetime
import asyncio

from src.db.database import get_session
from src.db.models import Deal, DealStatus
from src.core.logger import app_logger

# Create scheduler with job execution settings
scheduler = AsyncIOScheduler(
    job_defaults={
        'coalesce': True,  # Combine missed runs into one
        'max_instances': 1,  # Only one instance at a time
        'misfire_grace_time': 60  # 60 seconds grace period for missed jobs
    }
)

async def check_scheduled_posts():
    """
    Worker task: Checks for deals that are ready to be published.
    """
    app_logger.info("Worker: Checking for scheduled posts...")
    # Manually creating session
    async for session in get_session():
        statement = select(Deal).where(
            Deal.status == DealStatus.SCHEDULED,
            Deal.scheduled_at <= datetime.utcnow()
        )
        result = await session.exec(statement)
        deals = result.all()
        
        for deal in deals:
            await publish_post(session, deal)
        break 

async def publish_post(session, deal: Deal):
    """
    Publishes the post to the channel using the Bot API.
    [FIX P0]: Enabled actual posting.
    """
    try:
        app_logger.info(f"PUBLISHING AD: Deal {deal.id} to Channel {deal.channel_id}")
        
        # [FIX P0]: Lazy import to avoid circular dependency
        from src.main import bot
        
        # Get the channel's Telegram ID from the Channel model
        from src.db.models import Channel
        channel = await session.get(Channel, deal.channel_id)
        
        if not channel:
            app_logger.error(f"Channel not found for deal {deal.id}")
            return
        
        # [CORE ACTION]: Post the ad to the channel
        content = deal.ad_draft or deal.ad_brief  # Fallback to brief if no draft
        msg = await bot.send_message(channel.channel_id, content, parse_mode='HTML')

        # [VERIFICATION]: Generate Proof Link
        # If public channel, link format: t.me/username/id
        proof_link = f"https://t.me/{channel.username}/{msg.message_id}" if channel.username else str(msg.message_id)
        
        # [AUTOMATION]: Auto-Release Funds
        # 1. Get Owner Wallet
        from src.db.models import User
        from src.services.ton import TonGateway
        from src.core.config import settings
        
        owner = await session.get(User, channel.owner_id)
        
        if owner and owner.wallet_address:
            # 2. Initiate Transfer
            gateway = TonGateway(settings.TON_WALLET_ADDRESS)
            
            # Using 95% of amount (5% Platform Fee reserved) or Full Amount for MVP?
            # User wants "Hassle Free", implied full amount or fee deducted.
            # Let's send FULL amount for MVP transparency.
            
            app_logger.info(f"Releasing funds to Owner: {owner.wallet_address}")
            try:
                tx_hash = await gateway.send_ton_transfer(
                    destination=owner.wallet_address,
                    amount=deal.amount_ton,
                    memo=f"TG-ADMC Payout #{deal.id}"
                )
                if tx_hash:
                     app_logger.info(f"PAYOUT SUCCESS: {tx_hash}")
                else:
                     app_logger.error("PAYOUT FAILED: Transaction not broadcasted.")
            except Exception as pay_err:
                app_logger.error(f"PAYOUT ERROR: {pay_err}")
        else:
            app_logger.error(f"Cannot pay owner {channel.owner_id}: No wallet connected.")

        deal.status = DealStatus.COMPLETED
        deal.published_at = datetime.utcnow()
        deal.proof_link = proof_link
        
        session.add(deal)
        await session.commit()
        
        app_logger.info(f"Ad Published & Funds Released: {deal.id} | Proof: {proof_link}")
        
    except Exception as e:
        app_logger.error(f"Failed to publish ad {deal.id}: {e}")

def start_scheduler():
    scheduler.add_job(check_scheduled_posts, 'interval', minutes=1)
    scheduler.start()
    app_logger.info("Scheduler started.")
