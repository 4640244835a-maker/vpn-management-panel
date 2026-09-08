import base64
from fastapi import APIRouter, HTTPException, Response, Request
from app.api.users import USERS_DB

router = APIRouter(prefix="/sub", tags=["Subscription"])

@router.get("/{token}")
async def get_subscription(token: str, request: Request):
    user = next((u for u in USERS_DB if u["subscription_token"] == token), None)
    if not user:
        raise HTTPException(status_code=404, detail="Subscription token invalid or revoked")
    user_uuid = user["uuid"]
    username = user["username"]
    domain = "fra.node.railway.app"
    configs = [
        f"vless://{user_uuid}@{domain}:443?encryption=none&security=reality&sni=www.microsoft.com&fp=chrome&pbk=1y2x3w4v5u6t7s8r9q0p-reality-public-key&type=tcp#{username}-VLESS-Reality",
        f"trojan://{user_uuid}@{domain}:8443?security=tls&type=grpc&serviceName=trojan-grpc&sni={domain}#{username}-Trojan-gRPC"
    ]
    payload_b64 = base64.b64encode("\n".join(configs).encode("utf-8")).decode("utf-8")
    return Response(content=payload_b64, media_type="text/plain; charset=utf-8")
