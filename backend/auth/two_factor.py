"""
Two-Factor Authentication: TOTP (Google Authenticator compatible) + backup codes.
"""
from __future__ import annotations

import base64
import io
import secrets

import pyotp
import qrcode
import structlog

from core.config import settings

log = structlog.get_logger()


def generate_totp_secret() -> str:
    return pyotp.random_base32()


def get_totp_uri(secret: str, email: str) -> str:
    return pyotp.totp.TOTP(secret).provisioning_uri(
        name=email,
        issuer_name=settings.TOTP_ISSUER,
    )


def generate_qr_code_base64(totp_uri: str) -> str:
    img = qrcode.make(totp_uri)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")


def verify_totp(secret: str, code: str) -> bool:
    totp = pyotp.TOTP(secret)
    # Allow 1-step window (30s before/after) to handle clock drift
    return totp.verify(code, valid_window=1)


def generate_backup_codes(count: int = 10) -> list[str]:
    """Generate one-time backup codes."""
    return [secrets.token_hex(4).upper() for _ in range(count)]


def hash_backup_code(code: str) -> str:
    import hashlib
    return hashlib.sha256(code.encode()).hexdigest()


def verify_backup_code(plain: str, hashed_codes: list[str]) -> tuple[bool, list[str]]:
    """Verify and consume a backup code. Returns (valid, remaining_codes)."""
    hashed_input = hash_backup_code(plain.upper().replace("-", "").replace(" ", ""))
    if hashed_input in hashed_codes:
        remaining = [c for c in hashed_codes if c != hashed_input]
        return True, remaining
    return False, hashed_codes


def setup_2fa(email: str) -> dict:
    secret = generate_totp_secret()
    uri = get_totp_uri(secret, email)
    qr_code = generate_qr_code_base64(uri)
    backup_codes = generate_backup_codes()
    hashed_backup = [hash_backup_code(c) for c in backup_codes]

    return {
        "secret": secret,
        "qr_code_url": f"data:image/png;base64,{qr_code}",
        "backup_codes": backup_codes,
        "hashed_backup_codes": hashed_backup,
    }
