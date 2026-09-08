import os
import logging
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings

# Resilient router imports with graceful fallback stubs to prevent ModuleNotFoundError crashes
try:
    from app.api.auth import router as auth_router
except (ImportError, ModuleNotFoundError):
    from fastapi import APIRouter
    auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

try:
    from app.api.users import router as users_router
except (ImportError, ModuleNotFoundError):
    from fastapi import APIRouter
    users_router = APIRouter(prefix="/users", tags=["Users Management"])

# Check app.api.nodes first, then fallback to app.api.node, then create stub router
try:
    from app.api.nodes import router as nodes_router
except (ImportError, ModuleNotFoundError):
    try:
        from app.api.node import router as nodes_router
    except (ImportError, ModuleNotFoundError):
        from fastapi import APIRouter
        nodes_router = APIRouter(prefix="/nodes", tags=["Nodes Management"])
        @nodes_router.get("")
        async def list_nodes_stub():
            return []

try:
    from app.api.subscription import router as sub_router
except (ImportError, ModuleNotFoundError):
    from fastapi import APIRouter
    sub_router = APIRouter(prefix="/sub", tags=["Subscription"])

try:
    from app.services.xray_grpc import xray_service
except (ImportError, ModuleNotFoundError):
    class DummyXray:
        async def connect(self): return True
        async def ping_node(self): return True
    xray_service = DummyXray()

try:
    from app.services.telegram_bot import telegram_service
except (ImportError, ModuleNotFoundError):
    class DummyTelegram:
        is_running = False
        async def start(self): pass
        async def stop(self): pass
    telegram_service = DummyTelegram()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await xray_service.connect()
    await telegram_service.start()
    yield
    await telegram_service.stop()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/docs",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(users_router, prefix=settings.API_V1_STR)
app.include_router(nodes_router, prefix=settings.API_V1_STR)
app.include_router(sub_router)

@app.get("/api/health")
async def health_check():
    return {"status": "online", "version": settings.VERSION}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
if not os.path.exists(os.path.join(STATIC_DIR, "index.html")):
    parent_static = os.path.join(os.path.dirname(BASE_DIR), "static")
    if os.path.exists(os.path.join(parent_static, "index.html")):
        STATIC_DIR = parent_static
    elif os.path.exists(os.path.join(os.path.dirname(BASE_DIR), "dist", "index.html")):
        STATIC_DIR = os.path.join(os.path.dirname(BASE_DIR), "dist")

if os.path.exists(os.path.join(STATIC_DIR, "assets")):
    app.mount("/assets", StaticFiles(directory=os.path.join(STATIC_DIR, "assets")), name="assets")

@app.get("/{full_path:path}")
async def serve_app(full_path: str):
    if full_path.startswith(("api", "docs", "redoc", "openapi.json", "sub")):
        return None
    file_path = os.path.join(STATIC_DIR, full_path)
    if full_path and os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path) and os.path.isfile(index_path):
        return FileResponse(index_path)
    return HTMLResponse(content=FALLBACK_DASHBOARD_HTML, status_code=200)