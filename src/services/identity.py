from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import Optional, List

from src.db.models import User, Channel, UserRole
from src.core.logger import app_logger

class IdentityService:
    """
    Handles User Onboarding and Channel Verification.
    """
    def __init__(self, session: AsyncSession):
        self.session = session
        self.logger = app_logger

    async def get_or_create_user(self, telegram_id: int, username: str = None) -> User:
        """
        Retrieves a user by Telegram ID or creates a new one if not exists.
        [CONCURRENCY SAFE]: Handles race conditions via IntegrityError catch.
        """
        from sqlalchemy.exc import IntegrityError

        # 1. Optimistic Check
        statement = select(User).where(User.telegram_id == telegram_id)
        result = await self.session.exec(statement)
        user = result.first()
        
        if user:
            return user

        # 2. Create if missing
        try:
            user = User(telegram_id=telegram_id, username=username)
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
            self.logger.info(f"New User Created: {telegram_id}", extra={"user_id": user.id})
            return user
        except IntegrityError:
            # Race condition: User was created by another process between check and commit
            await self.session.rollback()
            self.logger.warning(f"Race condition detected for user {telegram_id}. Recovering...")
            
            # Retry fetch
            statement = select(User).where(User.telegram_id == telegram_id)
            result = await self.session.exec(statement)
            user = result.first()
            if not user:
                raise Exception("Critical: User creation failed and recovery failed.")
            return user

    async def register_channel(self, owner_id: int, channel_id: int, title: str) -> Channel:
        """
        [MODULAR COMPONENT]: Channel Onboarding
        Registers a new channel in the marketplace.
        
        Args:
            owner_id: Logic ID of the User who owns it.
            channel_id: Telegram's unique ID for the channel.
            title: Display name.
        """
        # Check if channel exists to avoid duplicates
        statement = select(Channel).where(Channel.channel_id == channel_id)
        result = await self.session.exec(statement)
        channel = result.first()
        
        if channel:
            self.logger.info(f"Channel already exists: {channel_id}")
            return channel

        channel = Channel(
            owner_id=owner_id,
            channel_id=channel_id,
            title=title,
            verified=False, 
            subscribers=0
        )
        try:
            self.session.add(channel)
            await self.session.commit()
            await self.session.refresh(channel)
        except Exception: # Catch IntegrityError (lazy import or use from above if global)
             # Fallback if somehow created in parallel
             await self.session.rollback()
             # Re-fetch
             statement = select(Channel).where(Channel.channel_id == channel_id)
             res = await self.session.exec(statement)
             return res.first()
        
        # [INTEGRATIVE]: Auto-add owner as a Manager
        await self.add_manager(channel.id, owner_id)
        
        self.logger.info(f"Channel Registered: {title} ({channel_id})", extra={"channel_id": channel.id})
        return channel

    async def add_manager(self, channel_db_id: int, user_db_id: int):
        """
        [MVP REQ]: PR Manager Flow
        Grants a user permission to manage a channel's ads.
        """
        from src.db.models import ChannelManager
        
        # Check if already a manager
        stmt = select(ChannelManager).where(
            ChannelManager.channel_id == channel_db_id,
            ChannelManager.user_id == user_db_id
        )
        res = await self.session.exec(stmt)
        if res.first():
            return

        manager = ChannelManager(user_id=user_db_id, channel_id=channel_db_id)
        try:
            self.session.add(manager)
            await self.session.commit()
            self.logger.info(f"Manager added: User {user_db_id} -> Channel {channel_db_id}")
        except Exception:
            await self.session.rollback()
            # Already exists, just ignore
            return

    async def verify_channel_stats(self, channel_id: int, stats: dict) -> Channel:
        """
        [MVP REQ]: Verified Stats Fetching
        Updates channel with real data from Telegram.
        
        Args:
            stats: Dictionary containing 'subscribers', 'avg_views', 'language', 'premium_ratio'.
        """
        channel = await self.session.get(Channel, channel_id)
        if not channel:
            raise ValueError("Channel not found")
        
        # Update fields dynamically
        channel.subscribers = stats.get("subscribers", channel.subscribers)
        channel.avg_views = stats.get("avg_views", channel.avg_views)
        channel.language = stats.get("language", channel.language)
        channel.premium_ratio = stats.get("premium_ratio", channel.premium_ratio)
        
        channel.verified = True
        channel.updated_at = datetime.utcnow()
        
        await self.session.commit()
        self.logger.info(f"Stats Updated for Channel: {channel.title}")
        return channel

    async def set_channel_price(self, channel_id: int, price: float) -> Channel:
        """
        [MVP REQ]: Set Channel Price
        Updates the asking price per post.
        """
        channel = await self.session.get(Channel, channel_id)
        if not channel:
            raise ValueError("Channel not found")
        
        channel.price_post = price
        channel.updated_at = datetime.utcnow()
        await self.session.commit()
        return channel
