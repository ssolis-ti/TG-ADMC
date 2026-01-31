"""
[ADMIN]: Demo/Test Endpoints for Hackathon Jury
Hidden admin panel for system management and testing.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime
import os

from src.db.database import get_session

admin_router = APIRouter(prefix="/admin", tags=["Admin"])

# [SECURITY]: Simple key for demo protection
ADMIN_KEY = os.getenv("ADMIN_KEY", "hackathon2026")

def verify_admin_key(key: str = Query(...)):
    if key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Invalid admin key")
    return True

# -------------------------------------------
# HEALTH CHECK
# -------------------------------------------
@admin_router.get("/health")
async def health_check(session: AsyncSession = Depends(get_session)):
    """
    [DEMO]: System health check for jury.
    Returns system status, DB connection, and timestamp.
    """
    try:
        # Test DB connection
        result = await session.execute(text("SELECT 1"))
        db_status = "connected" if result else "error"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": db_status,
        "version": "MVP-1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

# -------------------------------------------
# DATABASE RESET
# -------------------------------------------
@admin_router.post("/reset-db")
async def reset_database(key: str = Query(...), session: AsyncSession = Depends(get_session)):
    """
    [DEMO]: Reset database for fresh demo.
    Clears all Deals, preserves Channels and Users.
    Use key=hackathon2026 (or ADMIN_KEY env var).
    """
    if key != ADMIN_KEY:
        return {"error": "Invalid admin key", "hint": "Use ?key=hackathon2026"}
    
    try:
        # Clear deals (main transaction data)
        await session.execute(text("DELETE FROM deal"))
        await session.commit()
        
        return {
            "status": "success",
            "action": "database_reset",
            "cleared": ["deals"],
            "preserved": ["users", "channels"],
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        await session.rollback()
        return {"status": "error", "message": str(e)}

# -------------------------------------------
# FULL PURGE (Complete Reset)
# -------------------------------------------
@admin_router.post("/purge-all")
async def purge_all(key: str = Query(...), session: AsyncSession = Depends(get_session)):
    """
    [DEMO]: Complete system purge.
    Clears ALL data: Deals, Channels, Users.
    Use with caution - for fresh start demos only.
    """
    if key != ADMIN_KEY:
        return {"error": "Invalid admin key"}
    
    try:
        # Order matters due to foreign keys
        await session.execute(text("DELETE FROM deal"))
        await session.execute(text("DELETE FROM channel_manager"))
        await session.execute(text("DELETE FROM channel"))
        await session.execute(text("DELETE FROM \"user\""))
        await session.commit()
        
        return {
            "status": "success",
            "action": "full_purge",
            "cleared": ["deals", "channel_managers", "channels", "users"],
            "timestamp": datetime.utcnow().isoformat(),
            "message": "System is now clean for fresh demo"
        }
    except Exception as e:
        await session.rollback()
        return {"status": "error", "message": str(e)}

# -------------------------------------------
# SYSTEM INFO
# -------------------------------------------
@admin_router.get("/info")
async def system_info(session: AsyncSession = Depends(get_session)):
    """
    [DEMO]: System statistics for jury display.
    Shows counts of all entities.
    """
    try:
        users = await session.execute(text("SELECT COUNT(*) FROM \"user\""))
        channels = await session.execute(text("SELECT COUNT(*) FROM channel"))
        deals = await session.execute(text("SELECT COUNT(*) FROM deal"))
        
        return {
            "status": "ok",
            "stats": {
                "users": users.scalar(),
                "channels": channels.scalar(),
                "deals": deals.scalar()
            },
            "endpoints": {
                "health": "/admin/health",
                "reset_deals": "/admin/reset-db?key=<ADMIN_KEY>",
                "full_purge": "/admin/purge-all?key=<ADMIN_KEY>",
                "info": "/admin/info"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
