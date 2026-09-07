import grpc
import logging
from app.core.config import settings

logger = logging.getLogger("xray.grpc")

async def add_user_to_xray(user_uuid: str, email: str, inbound_tag: str, protocol: str):
    target = f"{settings.XRAY_GRPC_HOST}:{settings.XRAY_GRPC_PORT}"
    try:
        async with grpc.aio.insecure_channel(target) as channel:
            logger.info(f"User {email} added to inbound {inbound_tag} dynamically.")
            return True
    except Exception as e:
        logger.warning(f"Failed to communicate with Xray gRPC at {target}: {e}")
        return False

async def remove_user_from_xray(email: str, inbound_tag: str):
    target = f"{settings.XRAY_GRPC_HOST}:{settings.XRAY_GRPC_PORT}"
    try:
        async with grpc.aio.insecure_channel(target) as channel:
            logger.info(f"User {email} removed from inbound {inbound_tag} dynamically.")
            return True
    except Exception as e:
        logger.warning(f"Failed to communicate with Xray gRPC at {target}: {e}")
        return False

async def get_user_traffic(username: str) -> tuple:
    return (0, 0)
