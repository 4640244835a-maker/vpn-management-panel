import os
import logging
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
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
    description="FastAPI Backend & Xray-core Management Panel for Railway",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# 1. Comprehensive CORS Configuration for Frontend Dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# 2. Include API Routers FIRST
app.include_router(auth_router, prefix="/api/admin", tags=["Admin Auth"])
app.include_router(users_router, prefix="/api/user", tags=["User Operations"])
app.include_router(sub_router, prefix="/sub", tags=["Subscription Engine"])

# Healthcheck Endpoint
@app.get("/health", summary="Health Check")
async def health():
    return {
        "status": "ok",
        "service": "xray-vpn-manager",
        "cors": "enabled",
        "backend_url": "https://ali-production-6799.up.railway.app"
    }

# 3. Mount Static Frontend Assets & Catch-all SPA Route
STATIC_DIR = "static" if os.path.isdir("static") else "/app/static"

if os.path.exists(STATIC_DIR):
    assets_path = os.path.join(STATIC_DIR, "assets")
    if os.path.exists(assets_path):
        app.mount("/assets", StaticFiles(directory=assets_path), name="assets")

    @app.get("/{full_path:path}", summary="Catch-all SPA Frontend Routing")
    async def catch_all(full_path: str):
        # Ignore API routes, docs, and sub links so they are processed by FastAPI
        if (
            full_path.startswith("api")
            or full_path.startswith("sub")
            or full_path.startswith("docs")
            or full_path.startswith("redoc")
            or full_path.startswith("openapi.json")
            or full_path == "health"
        ):
            raise HTTPException(status_code=404, detail="Not Found")

        file_path = os.path.join(STATIC_DIR, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
            
        index_file = os.path.join(STATIC_DIR, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
            
        raise HTTPException(status_code=404, detail="Frontend static files not found")
