"""
RTK-1 FastAPI entry point — intentionally minimal.
"""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from prometheus_client import start_http_server

from app.api.v1.redteam import router as redteam_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.core.scheduler import scheduler

configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    asyncio.create_task(asyncio.to_thread(start_http_server, 8001))
    await scheduler.start()
    yield
    # Shutdown
    await scheduler.stop()


app = FastAPI(
    title="RTK-1 — Claude-Orchestrated AI Red Teaming API",
    description="Production-grade adversarial red-teaming: Claude 4 + LangGraph + PyRIT",
    version="0.5.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.mount("/reports", StaticFiles(directory="reports"), name="reports")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(redteam_router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "orchestrator": "Claude Sonnet 4.6 + LangGraph",
        "facade": "RTKFacade (PyRIT 0.12.0)",
        "environment": settings.environment,
        "version": "0.5.0",
        "scheduler": "active" if settings.scheduled_campaign_enabled else "disabled",
    }
