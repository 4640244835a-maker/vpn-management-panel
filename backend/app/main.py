import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import settings
from backend.app.db.session import engine, Base, AsyncSessionLocal
from backend.app.services.scheduler import start_scheduler, stop_scheduler
from backend.app.services.traffic_monitor import traffic_monitor
from backend.app.services.telegram_bot import telegram_bot
from backend.app.api.auth import router as auth_router
from backend.app.api.users import router as users_router
from backend.app.api.subscription import router as sub_router

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
    title="Marzban Xray VPN Manager API",
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