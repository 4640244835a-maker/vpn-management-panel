# Marzban-X VPN & Proxy Management Panel

A high-performance, modular VPN & proxy management suite built with **FastAPI**, **Xray-core gRPC**, and **React + Tailwind CSS**, ready for 1-click deployment on **Railway**.

## Features
- **Modern Protocols**: VLESS Reality (TCP/Vision), Trojan (gRPC/TLS), and VMess (WebSocket/TLS).
- **Multi-Node Cluster**: Real-time gRPC telemetry and user synchronization.
- **Automated Bot**: Telegram Bot integration with /stats, /create_user, and 80% quota alarms.
- **Bug-Free Deployment**: Configured with `start.sh`, `Procfile`, and root path import fixes.

## Quick Start on Railway
1. Connect this repository to Railway.
2. Railway detects `Dockerfile` or `Procfile`.
3. Set `PORT` (Railway injects automatically).
4. Access `https://<your-app>.railway.app` and log in with `admin` / `admin123`.