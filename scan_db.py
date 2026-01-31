import asyncio
from sqlalchemy import text
from src.db.database import get_session
from src.db.models import User, Channel, Deal
from sqlmodel import select, func

async def scan():
    print("🔍 **HUNTER SCAN INITIATED (DOCKER)**")
    print("==========================")
    
    async for session in get_session():
        # 1. User Stats
        n_users = (await session.exec(select(func.count(User.id)))).one()
        print(f"👤 Users: {n_users}")
        
        # 2. Channel Stats & Orphans
        channels = (await session.exec(select(Channel))).all()
        print(f"📢 Channels: {len(channels)}")
        for ch in channels:
            if not ch.owner_id:
                print(f"   ⚠️ ORPHAN CHANNEL: {ch.title} (ID: {ch.id}) has no owner!")
            else:
                owner = await session.get(User, ch.owner_id)
                if not owner:
                     print(f"   ⚠️ GHOST OWNER: Channel {ch.title} points to non-existent User {ch.owner_id}")

        # 3. Deal Stats & Integrity
        deals = (await session.exec(select(Deal))).all()
        print(f"🤝 Deals: {len(deals)}")
        
        for d in deals:
            status_icon = "🟢" if d.status == "completed" else "🟡" if d.status == "active" else "⚪"
            print(f"   {status_icon} Deal #{d.id}: {d.status.upper()} | {d.amount_ton} TON")
            
            if not d.advertiser_id:
                print(f"      ❌ INVALID: Deal #{d.id} has no advertiser!")
            
            if d.channel_id:
                 ch = await session.get(Channel, d.channel_id)
                 if not ch:
                     print(f"      ❌ INVALID: Deal #{d.id} points to missing Channel {d.channel_id}")

        # 4. Wallet Connectivity Check
        users_with_wallet = (await session.exec(select(func.count(User.id)).where(User.wallet_address != None))).one()
        print(f"💳 Wallets Connected: {users_with_wallet} / {n_users}")

        print("==========================")
        print("✅ SCAN COMPLETE")

if __name__ == "__main__":
    import sys
    import os
    # Add src to path
    sys.path.append(os.getcwd())
    asyncio.run(scan())
