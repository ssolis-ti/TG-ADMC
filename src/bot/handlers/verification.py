from aiogram import Router, types, F, Bot
from aiogram.filters import Command
from aiogram.enums import ChatType
from src.services.identity import IdentityService
from src.db.database import get_session
from src.db.database import get_session
from src.core.logger import app_logger
from src.core.config import settings

router = Router()

@router.message(Command("register"), F.chat.type.in_({ChatType.CHANNEL, ChatType.SUPERGROUP}))
async def cmd_register_channel(message: types.Message, bot: Bot):
    """ Legacy internal command """
    await register_channel_logic(message, bot, message.chat, message.from_user)

@router.message(F.chat.type == ChatType.PRIVATE)
async def handle_private_link(message: types.Message, bot: Bot):
    """ 
    [UX]: Smart Link Detection 
    Allows user to simply paste a channel link or username in private chat.
    """
    text = message.text.strip()
    
    # Simple extraction: Check for @username or t.me/username
    username = None
    if text.startswith("@"):
        username = text
    elif "t.me/" in text:
        username = "@" + text.split("t.me/")[-1].split("/")[0] # Crude but effective for MVP
    
    if not username:
        # Ignore normal chat messages to not be annoying, or handle help?
        # For now, only react if it looks like a channel
        return

    msg = await message.answer(f"🔍 Checking access to **{username}**...")
    
    try:
        # 1. Resolve Chat (Works if public or bot is member)
        chat = await bot.get_chat(username)
    except Exception:
        await msg.edit_text("❌ **Could not find channel.**\nMake sure the username is correct and I am an Admin there.")
        return

    # 2. Check Bot Admin Status
    try:
        bot_member = await bot.get_chat_member(chat.id, bot.id)
        if not bot_member.status in ("administrator", "creator"):
            await msg.edit_text(f"⚠️ **I am not an Admin in {chat.title}.**\n\nPlease add me as an Administrator with post permissions, then try again.")
            return
    except Exception:
         await msg.edit_text(f"⚠️ **Cannot access {username}.**\nPlease add me as Admin first.")
         return

    # 3. Check User Admin Status (Security)
    try:
        user_member = await bot.get_chat_member(chat.id, message.from_user.id)
        if not user_member.status in ("administrator", "creator"):
             await msg.edit_text("⛔ **You are not an Admin there.**\nOnly the owner or admins can register a channel.")
             return
    except Exception:
        await msg.edit_text("❓ **Could not verify your status.**")
        return

    # 4. Proceed to Registration
    await register_channel_logic(message, bot, chat, message.from_user, reply_message=msg)


async def register_channel_logic(message: types.Message, bot: Bot, chat: types.Chat, user: types.User, reply_message: types.Message = None):
    """ Shared Core Registration Logic """
    target_msg = reply_message if reply_message else message

    async for session in get_session():
        identity_service = IdentityService(session)
        # Ensure user exists
        owner = await identity_service.get_or_create_user(user.id, user.username)
        
        # Register Channel
        channel = await identity_service.register_channel(
            owner_id=owner.id,
            channel_id=chat.id,
            title=chat.title
        )
        
        # [AUTOMATIC]: Verification Logic
        sub_count = await bot.get_chat_member_count(chat.id)
        
        # Fallback Stats
        avg_views_est = int(sub_count * 0.25) 
        
        stats = {
            "subscribers": sub_count,
            "avg_views": avg_views_est,
            "language": "en", 
            "premium_ratio": 0.05
        }
        
        channel = await identity_service.verify_channel_stats(channel.id, stats)
        
        response_text = (
            f"✅ **Registration Successful!**\n\n"
            f"📢 **{channel.title}**\n"
            f"📊 Subs: {channel.subscribers} | Views: ~{channel.avg_views}\n\n"
            f"🚀 **Added to Marketplace.**"
        )

        # [UX]: Persistent Flow - Keypad to return to App
        kb = types.InlineKeyboardMarkup(inline_keyboard=[[
            types.InlineKeyboardButton(
                text="🔙 Open Marketplace",
                web_app=types.WebAppInfo(url=f"{settings.WEBHOOK_URL}/app")
            )
        ]])

        if reply_message:
            await reply_message.edit_text(response_text, reply_markup=kb)
        else:
            await message.answer(response_text, reply_markup=kb)
        break

@router.message(Command("setprice"), F.chat.type.in_({ChatType.CHANNEL, ChatType.SUPERGROUP}))
async def cmd_set_price(message: types.Message, bot: Bot):
    """
    [HANDLER] Set Price
    Usage: /setprice 50
    """
    args = message.text.split()
    if len(args) != 2:
        await message.answer("Usage: `/setprice <amount_ton>`\nExample: `/setprice 50`")
        return

    try:
        price = float(args[1])
        if price < 0.1:
            await message.answer("⚠️ Minimum price is 0.1 TON.")
            return
    except ValueError:
        await message.answer("❌ Invalid number.")
        return

    # Check Admin Status (User)
    try:
        user_member = await bot.get_chat_member(message.chat.id, message.from_user.id)
        if not user_member.status in ("administrator", "creator"):
            return 
    except:
        return

    async for session in get_session():
        # Quick update via service
        identity = IdentityService(session)
        # We need to find the channel by telegram ID first
        # Ideally we'd have a method 'get_channel_by_tg_id' but we can query directly
        from src.db.models import Channel
        from sqlmodel import select
        
        stmt = select(Channel).where(Channel.channel_id == message.chat.id)
        res = await session.exec(stmt)
        channel = res.first()
        
        if not channel:
            await message.answer("⚠️ Channel not registered yet! Use `/register` first.")
            return

        await identity.set_channel_price(channel.id, price)
        await message.answer(f"✅ **Price Updated!**\n\nNew verified price: **{price} TON** per post.")
        break
