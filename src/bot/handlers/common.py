from aiogram import Router, types
from aiogram.filters import CommandStart
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.identity import IdentityService
from src.db.database import get_session
from fastapi import Depends
from src.core.config import settings

router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    """
    Handles /start command.
    Registers the user and shows the Mini App button.
    """
    # Requires manual session handling since aiogram doesn't inject FastAPI dependencies directly
    async for session in get_session():
        identity_service = IdentityService(session)
        user = await identity_service.get_or_create_user(
            telegram_id=message.from_user.id,
            username=message.from_user.username
        )
        
        # [UX TIP 5D] Distinct Entry Point
        web_app_btn = types.KeyboardButton(
            text="🚀 Open Marketplace", 
            web_app=types.WebAppInfo(url=f"{settings.WEBHOOK_URL}/app") # Point to Frontend
        )
        keyboard = types.ReplyKeyboardMarkup(
            keyboard=[[web_app_btn]], 
            resize_keyboard=True
        )
        
        await message.answer(
            f"🎯 **Welcome to TG-ADMC Marketplace!**\n\n"
            f"The first decentralized ad marketplace for Telegram channels, powered by TON blockchain.\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"**📢 FOR ADVERTISERS:**\n"
            f"• Browse verified Telegram channels\n"
            f"• Pay securely with TON cryptocurrency\n"
            f"• Your funds are held in escrow until ad is published\n"
            f"• Get instant proof of publication\n\n"
            f"**💰 FOR CHANNEL OWNERS:**\n"
            f"• Monetize your audience safely\n"
            f"• Accept or reject ad requests\n"
            f"• Receive automatic payments in TON\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"**🚀 HOW TO GET STARTED:**\n\n"
            f"**As Advertiser:**\n"
            f"1️⃣ Click \"🚀 Open Marketplace\" below\n"
            f"2️⃣ Connect your TON wallet (Tonkeeper)\n"
            f"3️⃣ Browse channels and create your ad\n\n"
            f"**As Channel Owner:**\n"
            f"1️⃣ Add this bot as **Administrator** to your channel\n"
            f"2️⃣ **Send your channel link (e.g., @mychannel) here in the chat**\n"
            f"3️⃣ Open Marketplace to set your price\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👇 **Ready? Let's go!**",
            reply_markup=keyboard
        )
        break # Close generator
