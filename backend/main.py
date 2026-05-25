"""
AI Learning Platform - Main Application Entry Point
Production-grade FastAPI application with full microservice support
"""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import ORJSONResponse
from prometheus_client import make_asgi_app

from core.config import settings
from core.database import database_manager
from core.elasticsearch import es_manager
from core.kafka import kafka_manager
from core.redis import redis_manager
from core.telemetry import setup_telemetry
from api.v1.router import api_v1_router
from middleware.auth import AuthMiddleware
from middleware.logging import LoggingMiddleware
from middleware.rate_limit import RateLimitMiddleware
from middleware.request_id import RequestIDMiddleware
from middleware.security import SecurityHeadersMiddleware
from websocket.router import websocket_router

log = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application lifecycle: startup and shutdown."""
    log.info("Starting AI Learning Platform", version=settings.APP_VERSION, env=settings.APP_ENV)

    # Initialize infrastructure connections
    await database_manager.connect()
    await redis_manager.connect()
    try:
        await kafka_manager.connect()
    except Exception as exc:
        log.warning("Kafka unavailable — continuing without it", error=str(exc))
    try:
        await es_manager.connect()
    except Exception as exc:
        log.warning("Elasticsearch unavailable — continuing without it", error=str(exc))

    # Setup OpenTelemetry
    setup_telemetry()

    log.info("All services connected successfully")
    yield

    # Graceful shutdown
    log.info("Shutting down AI Learning Platform")
    await kafka_manager.disconnect()
    await es_manager.disconnect()
    await redis_manager.disconnect()
    await database_manager.disconnect()
    log.info("Shutdown complete")


def create_application() -> FastAPI:
    """Factory function to create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Production-grade AI-native technical learning platform",
        docs_url="/docs" if settings.APP_DEBUG else None,
        redoc_url="/redoc" if settings.APP_DEBUG else None,
        openapi_url="/openapi.json" if settings.APP_DEBUG else None,
        default_response_class=ORJSONResponse,
        lifespan=lifespan,
    )

    # ── Middleware (order matters: outermost wraps innermost) ─────────────────
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-RateLimit-Limit", "X-RateLimit-Remaining"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(AuthMiddleware)

    # ── Routers ───────────────────────────────────────────────────────────────
    app.include_router(api_v1_router, prefix="/api/v1")
    app.include_router(websocket_router, prefix="/ws")

    # ── Prometheus metrics endpoint ───────────────────────────────────────────
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)

    # ── Health endpoints ──────────────────────────────────────────────────────
    @app.get("/health", tags=["health"])
    async def health_check() -> dict:
        return {
            "status": "healthy",
            "version": settings.APP_VERSION,
            "environment": settings.APP_ENV,
        }

    @app.get("/health/ready", tags=["health"])
    async def readiness_check() -> dict:
        checks = {
            "database": await database_manager.health_check(),
            "redis": await redis_manager.health_check(),
            "kafka": await kafka_manager.health_check(),
            "elasticsearch": await es_manager.health_check(),
        }
        is_ready = all(checks.values())
        return {"status": "ready" if is_ready else "not_ready", "checks": checks}

    @app.get("/health/live", tags=["health"])
    async def liveness_check() -> dict:
        return {"status": "alive"}

    return app


app = create_application()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.APP_DEBUG,
        workers=1 if settings.APP_DEBUG else 4,
        log_config=None,  # use structlog
        access_log=False,
    )
