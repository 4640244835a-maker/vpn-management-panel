import os
import logging
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse, FileResponse, HTMLResponse
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

# 1. Comprehensive CORS Configuration
ALLOWED_ORIGINS = [
    "*",
    "https://ali-production-6799.up.railway.app",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# 2. Include API Routers
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

# 3. Mount Static Frontend (Option A)
STATIC_DIR = Path("/app/static")
if not STATIC_DIR.exists():
    # Local fallback
    STATIC_DIR = Path("static")

if STATIC_DIR.exists() and (STATIC_DIR / "index.html").exists():
    # Mount assets folder if exists
    assets_dir = STATIC_DIR / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="static_assets")

    @app.get("/dashboard", summary="Web Dashboard SPA")
    @app.get("/dashboard/{full_path:path}", summary="Web Dashboard Subpaths")
    async def serve_dashboard(full_path: str = ""):
        return FileResponse(str(STATIC_DIR / "index.html"))

# 4. Root Endpoint
@app.get("/", summary="Root Endpoint")
async def root(request: Request):
    # Check if compiled frontend index.html exists
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    
    # If accessed via a browser expecting HTML, redirect gracefully to /docs
    accept = request.headers.get("accept", "")
    if "text/html" in accept and not request.query_params.get("raw"):
        return RedirectResponse(url="/docs")
    
    return {
        "status": "ok",
        "message": "Marzban Xray VPN Manager API is running",
        "backend_url": "https://ali-production-6799.up.railway.app",
        "docs_url": "/docs",
        "openapi_url": "/openapi.json",
        "health_check": "/health",
        "dashboard_url": "/dashboard"
    }
