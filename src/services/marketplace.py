from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import List

from src.db.models import Channel
from src.core.logger import app_logger

class MarketplaceService:
    """
    Handles the 'Browsing' side of the marketplace.
    """
    def __init__(self, session: AsyncSession):
        self.session = session
        self.logger = app_logger

    async def list_verified_channels(self, limit: int = 10, offset: int = 0) -> List[Channel]:
        """
        Fetches verified channels for the marketplace listing.
        
        Logic:
        - Only returns channels where `verified=True`.
        - Supports pagination via `limit` and `offset`.
        
        Args:
            limit (int): Max number of channels to return.
            offset (int): Number of channels to skip.
            
        Returns:
            List[Channel]: List of verified channel objects.
        """
        # SQL: SELECT * FROM channel WHERE verified = 1 LIMIT x OFFSET y
        statement = select(Channel).where(Channel.verified == True).offset(offset).limit(limit)
        result = await self.session.exec(statement)
        channels = result.all()
        return list(channels)
