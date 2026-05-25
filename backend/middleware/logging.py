"""Structured request/response logging middleware using structlog."""
from __future__ import annotations

import time
import uuid

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

log = structlog.get_logger()


class LoggingMiddleware(BaseHTTPMiddleware):
    SKIP_PATHS = {"/health", "/health/ready", "/health/live", "/metrics"}

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path in self.SKIP_PATHS:
            return await call_next(request)

        start_time = time.perf_counter()
        request_id = request.state.request_id if hasattr(request.state, "request_id") else str(uuid.uuid4())

        # Bind request context to structlog
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host if request.client else "unknown",
        )

        try:
            response = await call_next(request)
            duration_ms = (time.perf_counter() - start_time) * 1000

            log.info(
                "HTTP request",
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2),
            )
            response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"
            return response
        except Exception as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000
            log.error("HTTP request failed", error=str(exc), duration_ms=round(duration_ms, 2))
            raise
        finally:
            structlog.contextvars.clear_contextvars()
