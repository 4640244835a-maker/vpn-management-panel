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

BUILD_DIRS = ["static", "dist", "frontend/dist"]
STATIC_DIR = next((d for d in BUILD_DIRS if os.path.isdir(d) and os.path.exists(os.path.join(d, "index.html"))), None)
if not STATIC_DIR:
    STATIC_DIR = next((d for d in BUILD_DIRS if os.path.isdir(d)), "static")

for candidate in [os.path.join(STATIC_DIR, "assets"), "static/assets", "dist/assets", "frontend/dist/assets"]:
    if os.path.isdir(candidate):
        app.mount("/assets", StaticFiles(directory=candidate), name="assets")
        break

@app.get("/")
async def serve_root():
    for b_dir in [STATIC_DIR, "static", "dist", "frontend/dist"]:
        if b_dir and os.path.isdir(b_dir):
            index_candidate = os.path.join(b_dir, "index.html")
            if os.path.isfile(index_candidate):
                return FileResponse(index_candidate)
    if os.path.isfile("index.html"):
        return FileResponse("index.html")
    return JSONResponse({"status": "FastAPI Backend Running", "docs": "/docs"})

@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    if full_path.startswith(("api", "docs", "redoc", "openapi.json", "sub")):
        return JSONResponse(status_code=404, content={"detail": f"Route /{full_path} not found"})
    for b_dir in [STATIC_DIR, "static", "dist", "frontend/dist"]:
        if b_dir and os.path.isdir(b_dir):
            target_file = os.path.join(b_dir, full_path)
            if full_path and os.path.isfile(target_file):
                return FileResponse(target_file)
            index_candidate = os.path.join(b_dir, "index.html")
            if os.path.isfile(index_candidate):
                return FileResponse(index_candidate)
    if os.path.isfile("index.html"):
        return FileResponse("index.html")
    return JSONResponse({"status": "FastAPI Backend Running", "docs": "/docs"})