"""Lightweight WAF (Web Application Firewall) middleware.

Provides:
- SQL injection pattern detection
- XSS payload detection
- Path traversal detection
- Oversized payload rejection
- Suspicious User-Agent blocking
"""
from __future__ import annotations

import re
from typing import Callable

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

log = structlog.get_logger()

# Compiled regex patterns for performance
_SQL_INJECTION = re.compile(
    r"(?i)(\b(select|insert|update|delete|drop|truncate|alter|exec|execute|union|"
    r"declare|cast|convert|char|nchar|varchar|nvarchar|xp_|sp_)\b"
    r"|--|;.*--|\bor\b\s+\d+\s*=\s*\d+|\bor\b\s+'[^']*'\s*=\s*'[^']*')",
    re.IGNORECASE,
)

_XSS = re.compile(
    r"(?i)(<\s*script[^>]*>|javascript\s*:|on\w+\s*=|"
    r"<\s*iframe|<\s*object|<\s*embed|data:\s*text/html)",
    re.IGNORECASE,
)

_PATH_TRAVERSAL = re.compile(r"\.\./|\.\.\\|%2e%2e%2f|%2e%2e/|\.\./|%252e%252e", re.IGNORECASE)

_SUSPICIOUS_UA = re.compile(
    r"(?i)(sqlmap|nikto|nessus|masscan|zgrab|dirbuster|gobuster|"
    r"nuclei|acunetix|burpsuite|nmap|havij|pangolin)",
    re.IGNORECASE,
)

# Paths that are never scanned (e.g. binary uploads)
_SKIP_BODY_SCAN_PATHS = frozenset({"/api/v1/storage/upload"})

MAX_BODY_SIZE = 10 * 1024 * 1024  # 10 MB


class WAFMiddleware(BaseHTTPMiddleware):
    """Inspect incoming requests for common attack patterns."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # --- Block suspicious User-Agents ---
        ua = request.headers.get("user-agent", "")
        if _SUSPICIOUS_UA.search(ua):
            log.warning("WAF: blocked suspicious UA", ua=ua, path=request.url.path)
            return JSONResponse({"detail": "Forbidden"}, status_code=403)

        # --- Check URL path for traversal ---
        path = str(request.url)
        if _PATH_TRAVERSAL.search(path):
            log.warning("WAF: path traversal attempt", path=path)
            return JSONResponse({"detail": "Forbidden"}, status_code=403)

        # --- Check query string ---
        qs = str(request.url.query)
        if _SQL_INJECTION.search(qs) or _XSS.search(qs):
            log.warning("WAF: attack pattern in query string", qs=qs[:200], path=request.url.path)
            return JSONResponse({"detail": "Bad Request"}, status_code=400)

        # --- Inspect request body for POST/PUT/PATCH ---
        if request.method in ("POST", "PUT", "PATCH") and request.url.path not in _SKIP_BODY_SCAN_PATHS:
            content_length = int(request.headers.get("content-length", 0))
            if content_length > MAX_BODY_SIZE:
                log.warning("WAF: oversized body", size=content_length, path=request.url.path)
                return JSONResponse({"detail": "Payload too large"}, status_code=413)

            content_type = request.headers.get("content-type", "")
            if "application/json" in content_type or "application/x-www-form-urlencoded" in content_type:
                try:
                    body = await request.body()
                    body_str = body.decode("utf-8", errors="replace")
                    if _SQL_INJECTION.search(body_str) or _XSS.search(body_str):
                        log.warning(
                            "WAF: attack pattern in body",
                            path=request.url.path,
                            preview=body_str[:200],
                        )
                        return JSONResponse({"detail": "Bad Request"}, status_code=400)
                except Exception:
                    pass  # Don't crash on decode errors

        return await call_next(request)
