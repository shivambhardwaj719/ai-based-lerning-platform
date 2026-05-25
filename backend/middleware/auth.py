"""Auth middleware: extracts user from JWT and attaches to request state."""
from __future__ import annotations

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from auth.jwt import get_token_from_header, verify_access_token


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        authorization = request.headers.get("Authorization")
        token = get_token_from_header(authorization)

        if token:
            try:
                payload = await verify_access_token(token)
                request.state.user_id = payload.get("sub")
                request.state.user_role = payload.get("role")
                request.state.session_id = payload.get("sid")
            except Exception:
                request.state.user_id = None
                request.state.user_role = None
        else:
            request.state.user_id = None
            request.state.user_role = None

        return await call_next(request)
