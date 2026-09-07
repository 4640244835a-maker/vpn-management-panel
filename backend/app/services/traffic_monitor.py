import asyncio
import logging
from sqlalchemy.future import select
from app.db.session import AsyncSessionLocal
from app.models.user import User, UserStatus
from app.services.xray import get_user_traffic, remove_user_from_xray
from app.services.telegram_bot import telegram_bot

logger = logging.getLogger("xray.traffic_monitor")

class TrafficMonitor:
    def __init__(self, interval_seconds: int = 30):
        self.interval = interval_seconds
        self.running = False
        self._task = None

    def start(self):
        if not self.running:
            self.running = True
            self._task = asyncio.create_task(self._run_loop())
            logger.info("Traffic monitor background task started.")

    async def stop(self):
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            logger.info("Traffic monitor stopped.")

    async def _run_loop(self):
        while self.running:
            try:
                await self.sync_cycle()
            except Exception as e:
                logger.error(f"Error in traffic monitor sync cycle: {e}")
            await asyncio.sleep(self.interval)

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

traffic_monitor = TrafficMonitor()
