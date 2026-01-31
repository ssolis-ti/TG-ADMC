from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from src.core.config import settings

# Create Async Engine
# echo=True will log all SQL queries for debugging (solid debugging principle)
engine = create_async_engine(settings.DATABASE_URL, echo=True, future=True)

async def init_db():
    """
    Creates the database tables based on SQLModel definitions.
    Should be run on startup.
    """
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_session() -> AsyncSession:
    """
    Dependency for FastAPI/Bot to get a DB session.
    """
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
