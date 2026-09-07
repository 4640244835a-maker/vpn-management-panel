import logging
from typing import Optional
from app.core.config import settings
from app.models.user import User

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
        try:
            from telegram.ext import ApplicationBuilder
            self.application = ApplicationBuilder().token(self.token).build()
            await self.application.initialize()
            await self.application.start()
            if self.application.updater:
                await self.application.updater.start_polling()
            logger.info("Telegram bot service started successfully.")
        except Exception as e:
            logger.warning(f"Could not start Telegram Bot: {e}")

    async def stop(self):
        if self.application:
            try:
                if self.application.updater and self.application.updater.running:
                    await self.application.updater.stop()
                await self.application.stop()
                await self.application.shutdown()
            except Exception as e:
                logger.warning(f"Error while stopping Telegram Bot: {e}")

    async def send_notification(self, msg: str):
        if not self.application or not self.admin_chat_id:
            logger.info(f"[Bot Alert]: {msg}")
            return
        try:
            await self.application.bot.send_message(
                chat_id=self.admin_chat_id,
                text=msg,
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.warning(f"Failed to send Telegram alert: {e}")

    async def send_traffic_warning_alert(self, user: User, percent: float):
        msg = f"⚠️ *هشدار مصرف ۸۰٪*: کاربر {user.username} {percent:.1f}% حجم خود را مصرف کرده است."
        await self.send_notification(msg)

    async def send_account_limited_alert(self, user: User):
        msg = f"🚫 *قطع ترافیک*: حجم کاربر {user.username} به اتمام رسید و در هسته غیرفعال شد."
        await self.send_notification(msg)

telegram_bot = TelegramBotService()
