from __future__ import annotations

import asyncio
import logging
import os
from pathlib import Path
import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from src.api.chat import router as chat_router

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")

# Load skill definitions from skills/ directory at startup
from src.skills import load_skills
load_skills()

app = FastAPI(title="GAI-PLA API", description="Generative AI-Based Personalized Learning Agent", version="0.1.0")

# CORS: read ALLOWED_ORIGINS from .env; allow all by default (development).
# In production, set ALLOWED_ORIGINS=https://yourdomain.com,https://another.com
_origins = os.environ.get("ALLOWED_ORIGINS", "*")
_origin_list = ["*"] if _origins == "*" else [o.strip() for o in _origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origin_list,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

app.include_router(chat_router, prefix="/api")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.on_event("startup")
async def start_keep_alive():
    """Background task to keep Render free tier alive by pinging the external health URL."""
    external_url = os.environ.get("RENDER_EXTERNAL_URL") or os.environ.get("KEEP_ALIVE_URL")
    if not external_url:
        logging.info("[Keep-Alive] No external URL configured; skipping keep-alive worker.")
        return

    interval = int(os.environ.get("KEEP_ALIVE_INTERVAL_SECONDS", "300"))
    health_url = f"{external_url.rstrip('/')}/health"

    async def keep_alive_loop():
        await asyncio.sleep(20)
        logging.info(f"[Keep-Alive] Worker active: pinging {health_url} every {interval}s")
        async with httpx.AsyncClient(timeout=10.0) as client:
            while True:
                try:
                    r = await client.get(health_url)
                    logging.info(f"[Keep-Alive] Self-ping {health_url} -> {r.status_code}")
                except Exception as e:
                    logging.warning(f"[Keep-Alive] Ping failed: {e}")
                await asyncio.sleep(interval)

    asyncio.create_task(keep_alive_loop())


# Static files must be mounted AFTER all API routes
_static_dir = Path(__file__).resolve().parent.parent / "static"
app.mount("/", StaticFiles(directory=str(_static_dir), html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("run.serve:app", host="0.0.0.0", port=8080, reload=True)
