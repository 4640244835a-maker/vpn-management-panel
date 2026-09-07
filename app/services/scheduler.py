import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler

logger = logging.getLogger("xray.scheduler")
scheduler = AsyncIOScheduler()

def start_scheduler():
    try:
        if not scheduler.running:
            scheduler.start()
            logger.info("APScheduler background scheduler started.")
    except Exception as e:
        logger.warning(f"Could not start scheduler: {e}")

def stop_scheduler():
    try:
        if scheduler.running:
            scheduler.shutdown(wait=False)
            logger.info("APScheduler stopped.")
    except Exception as e:
        logger.warning(f"Could not stop scheduler: {e}")
