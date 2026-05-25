"""Password hashing and OTP generation."""
from __future__ import annotations

import secrets
import string

from passlib.context import CryptContext

from core.config import settings
from core.redis import redis_manager

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=settings.PASSWORD_HASH_ROUNDS,
)


def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def generate_otp(length: int = 6) -> str:
    return "".join(secrets.choice(string.digits) for _ in range(length))


async def store_otp(identifier: str, otp: str, ttl: int = 600) -> None:
    await redis_manager.set(f"otp:{identifier}", otp, ttl=ttl)


async def verify_otp(identifier: str, code: str) -> bool:
    stored = await redis_manager.get(f"otp:{identifier}")
    if stored and secrets.compare_digest(str(stored), code):
        await redis_manager.delete(f"otp:{identifier}")
        return True
    return False
