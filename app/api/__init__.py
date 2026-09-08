try:
    from app.api.auth import router as auth_router
except (ImportError, ModuleNotFoundError):
    auth_router = None

try:
    from app.api.users import router as users_router
except (ImportError, ModuleNotFoundError):
    users_router = None

try:
    from app.api.nodes import router as nodes_router
except (ImportError, ModuleNotFoundError):
    try:
        from app.api.node import router as nodes_router
    except (ImportError, ModuleNotFoundError):
        from fastapi import APIRouter
        nodes_router = APIRouter(prefix="/nodes", tags=["Nodes Management"])

node_router = nodes_router

try:
    from app.api.subscription import router as sub_router
except (ImportError, ModuleNotFoundError):
    sub_router = None

__all__ = ["auth_router", "users_router", "nodes_router", "node_router", "sub_router"]
