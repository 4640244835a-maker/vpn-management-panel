from typing import List
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/nodes", tags=["Nodes Management"])

class NodeStats(BaseModel):
    id: int
    name: str
    address: str
    port: int
    status: str
    latency_ms: int
    core_version: str
    cpu_percent: float
    mem_percent: float
    uptime_days: int
    active_users: int
    protocols: List[str]

NODES_CACHE = [
    {
        "id": 1,
        "name": "Frankfurt Edge 01 (Master)",
        "address": "fra-node1.network-edge.io",
        "port": 10085,
        "status": "online",
        "latency_ms": 38,
        "core_version": "Xray-core 1.8.8",
        "cpu_percent": 18.4,
        "mem_percent": 42.1,
        "uptime_days": 28,
        "active_users": 64,
        "protocols": ["VLESS Reality", "VMess WS", "Trojan gRPC"]
    },
    {
        "id": 2,
        "name": "Amsterdam High-Bandwidth 02",
        "address": "ams-node2.network-edge.io",
        "port": 10085,
        "status": "online",
        "latency_ms": 44,
        "core_version": "Xray-core 1.8.8",
        "cpu_percent": 24.2,
        "mem_percent": 55.0,
        "uptime_days": 19,
        "active_users": 52,
        "protocols": ["VLESS Reality", "VMess TCP", "Shadowsocks 2022"]
    }
]

@router.get("", response_model=List[NodeStats])
async def list_nodes():
    return NODES_CACHE
