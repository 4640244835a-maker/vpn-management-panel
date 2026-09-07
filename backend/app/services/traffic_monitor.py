import asyncio, logging
from datetime import datetime
from sqlalchemy.future import select
from backend.app.db.session import AsyncSessionLocal
from backend.app.models.user import User, UserStatus
from backend.app.services.xray import get_user_traffic, remove_user_from_xray
from backend.app.services.telegram_bot import telegram_bot

logger = logging.getLogger("xray.traffic_monitor")

class TrafficMonitor:
    def __init__(self, interval_seconds: int = 30):
        self.interval = interval_seconds
        self.running = False

    async def sync_cycle(self):
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(User).where(User.status == UserStatus.ACTIVE))
            active_users = result.scalars().all()
            for user in active_users:
                up, down = await get_user_traffic(user.username)
                user.used_traffic += (up + down)
                
                # Check Expiration & Quota
                if user.data_limit and user.used_traffic >= user.data_limit:
                    user.status = UserStatus.LIMITED
                    for inbound in user.inbounds:
                        await remove_user_from_xray(user.username, inbound.tag)
                    await telegram_bot.send_account_limited_alert(user)
            await db.commit()