"""
JWT token management: access tokens, refresh tokens, blacklisting.
Uses HS256 signing with JTI-based invalidation via Redis.
"""
from __future__ import annotations

import hashlib
import secrets
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt

from core.config import settings
from core.exceptions import InvalidTokenError, TokenExpiredError
from core.redis import redis_manager


class TokenType:
    ACCESS = "access"
    REFRESH = "refresh"
    EMAIL_VERIFY = "email_verify"
    PASSWORD_RESET = "password_reset"
    OTP = "otp"


def _create_token(payload: dict[str, Any], expires_delta: timedelta) -> str:
    expire = datetime.now(UTC) + expires_delta
    to_encode = {
        **payload,
        "exp": expire,
        "iat": datetime.now(UTC),
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token(
    user_id: uuid.UUID,
    role: str,
    session_id: uuid.UUID | None = None,
    extra: dict | None = None,
) -> tuple[str, str]:
    """Returns (token, jti) tuple."""
    jti = str(uuid.uuid4())
    payload: dict = {
        "sub": str(user_id),
        "type": TokenType.ACCESS,
        "role": role,
        "jti": jti,
    }
    if session_id:
        payload["sid"] = str(session_id)
    if extra:
        payload.update(extra)

    expire = datetime.now(UTC) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {**payload, "exp": expire, "iat": datetime.now(UTC)}
    token = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token, jti


def create_refresh_token() -> tuple[str, str]:
    """Returns (raw_token, hashed_token) for DB storage."""
    raw = secrets.token_urlsafe(64)
    hashed = _hash_token(raw)
    return raw, hashed


def create_email_verify_token(user_id: uuid.UUID) -> str:
    return _create_token(
        {"sub": str(user_id), "type": TokenType.EMAIL_VERIFY},
        timedelta(hours=24),
    )


def create_password_reset_token(user_id: uuid.UUID) -> str:
    return _create_token(
        {"sub": str(user_id), "type": TokenType.PASSWORD_RESET},
        timedelta(hours=1),
    )


def create_otp_token(email: str) -> str:
    return _create_token(
        {"email": email, "type": TokenType.OTP},
        timedelta(minutes=10),
    )


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


async def verify_access_token(token: str) -> dict:
    """Verify access token; raise on expiry or invalidity."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except jwt.ExpiredSignatureError:
        raise TokenExpiredError()
    except JWTError:
        raise InvalidTokenError()

    if payload.get("type") != TokenType.ACCESS:
        raise InvalidTokenError()

    jti = payload.get("jti")
    if jti and await _is_token_blacklisted(jti):
        raise InvalidTokenError()

    return payload


async def verify_token(token: str, expected_type: str) -> dict:
    """Verify a single-use token (email verify, password reset)."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except jwt.ExpiredSignatureError:
        raise TokenExpiredError()
    except JWTError:
        raise InvalidTokenError()

    if payload.get("type") != expected_type:
        raise InvalidTokenError()

    jti = payload.get("jti", "")
    if await _is_token_blacklisted(jti):
        raise InvalidTokenError()

    return payload


async def blacklist_token(jti: str, expires_in_seconds: int) -> None:
    await redis_manager.set(f"blacklist:token:{jti}", "1", ttl=expires_in_seconds)


async def _is_token_blacklisted(jti: str) -> bool:
    return await redis_manager.exists(f"blacklist:token:{jti}")


def get_token_from_header(authorization: str | None) -> str | None:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    return authorization[7:]
