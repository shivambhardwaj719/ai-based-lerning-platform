"""
Sliding window rate limiter middleware with Redis backend.
Supports per-IP and per-user rate limits with different tiers.
"""
from __future__ import annotations

import time

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from core.config import settings
from core.redis import redis_manager


class RateLimitMiddleware(BaseHTTPMiddleware):
    SKIP_PATHS = {"/health", "/health/ready", "/health/live", "/metrics", "/docs", "/openapi.json"}

    # Stricter limits for auth endpoints
    AUTH_PATHS = {"/api/v1/auth/login", "/api/v1/auth/register", "/api/v1/auth/forgot-password"}

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path in self.SKIP_PATHS:
            return await call_next(request)

        # Determine rate limit key and limits
        client_ip = request.client.host if request.client else "unknown"
        is_auth_path = any(request.url.path.startswith(p) for p in self.AUTH_PATHS)

        if is_auth_path:
            limit = settings.RATE_LIMIT_AUTH_PER_MINUTE
            window = 60
            key = f"rl:auth:{client_ip}"
        else:
            limit = settings.RATE_LIMIT_PER_MINUTE
            window = 60
            user_id = getattr(request.state, "user_id", None)
            key = f"rl:user:{user_id}" if user_id else f"rl:ip:{client_ip}"

        allowed, remaining = await redis_manager.rate_limit_check(key, limit, window)

        if not allowed:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded"},
                headers={
                    "Retry-After": "60",
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                },
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response
