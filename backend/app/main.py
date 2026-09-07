import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.session import engine, Base
from app.services.scheduler import start_scheduler, stop_scheduler
from app.services.traffic_monitor import traffic_monitor
from app.services.telegram_bot import telegram_bot
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.subscription import router as sub_router

logger = logging.getLogger("xray.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # Start background scheduler, traffic monitor and telegram bot
    start_scheduler()
    traffic_monitor.start()
    await telegram_bot.start()
    
    yield
    
    await telegram_bot.stop()
    await traffic_monitor.stop()
    stop_scheduler()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/admin", tags=["Admin Auth"])
app.include_router(users_router, prefix="/api/user", tags=["User Operations"])
app.include_router(sub_router, prefix="/sub", tags=["Subscription Engine"])

@app.get("/health")
async def health():
    return {"status": "ok", "service": "xray-vpn-manager"}
