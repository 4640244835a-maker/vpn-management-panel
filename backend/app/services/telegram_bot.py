import logging
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.future import select
from backend.app.core.config import settings
from backend.app.db.session import AsyncSessionLocal
from backend.app.models.user import User, UserStatus
from backend.app.services.xray import add_user_to_xray

logger = logging.getLogger("telegram_bot")

class TelegramBotService:
    def __init__(self):
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.admin_chat_id = settings.TELEGRAM_ADMIN_CHAT_ID
        self.application = None

    async def start(self):
        if not self.token:
            logger.info("Telegram Bot token not set. Skipping bot startup.")
            return
        from telegram.ext import ApplicationBuilder, CommandHandler
        self.application = ApplicationBuilder().token(self.token).build()
        # Handlers for /start, /stats, /create_user, /find_user ...
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()

    async def send_traffic_warning_alert(self, user: User, percent: float):
        msg = f"⚠️ *هشدار مصرف ۸۰٪*: کاربر {user.username} {percent:.1f}% حجم خود را مصرف کرده است."
        await self.send_notification(msg)

    async def send_account_limited_alert(self, user: User):
        msg = f"🚫 *قطع ترافیک*: حجم کاربر {user.username} به اتمام رسید و در هسته غیرفعال شد."
        await self.send_notification(msg)

telegram_bot = TelegramBotService()