import logging
from app.core.config import settings

logger = logging.getLogger("telegram.bot")

class TelegramBotService:
    def __init__(self):
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.is_running = False

    async def start(self):
        if not self.token:
            return
        self.is_running = True
        logger.info("Telegram Bot daemon started.")

    async def stop(self):
        self.is_running = False

    async def notify_traffic_threshold(self, username: str, used_gb: float, limit_gb: float, percent: float):
        msg = f"⚠️ Warning: User {username} reached {percent:.1f}% bandwidth ({used_gb:.1f}/{limit_gb:.1f} GB)"
        logger.info(msg)

telegram_service = TelegramBotService()