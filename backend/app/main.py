import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
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

# Comprehensive CORS Configuration for Frontend Integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Root Endpoint: Return API status and redirect helper
@app.get("/", summary="Root Endpoint")
async def root(request: Request):
    # If accessed via a browser expecting HTML, redirect gracefully to Swagger UI /docs
    accept = request.headers.get("accept", "")
    if "text/html" in accept and not request.query_params.get("raw"):
        return RedirectResponse(url="/docs")
    return {
        "status": "ok",
        "message": "API is running",
        "service": settings.PROJECT_NAME,
        "docs_url": "/docs",
        "openapi_url": "/openapi.json",
        "health_check": "/health"
    }

# Healthcheck Endpoint
@app.get("/health", summary="Health Check")
async def health():
    return {
        "status": "ok",
        "service": "xray-vpn-manager",
        "cors": "enabled"
    }

# Include API Routers
app.include_router(auth_router, prefix="/api/admin", tags=["Admin Auth"])
app.include_router(users_router, prefix="/api/user", tags=["User Operations"])
app.include_router(sub_router, prefix="/sub", tags=["Subscription Engine"])
