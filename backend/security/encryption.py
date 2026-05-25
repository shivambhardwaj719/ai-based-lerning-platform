"""Field-level encryption using Fernet symmetric encryption."""
from __future__ import annotations

import base64

from cryptography.fernet import Fernet

from core.config import settings


def _get_fernet() -> Fernet:
    key = settings.ENCRYPTION_KEY.encode() if settings.ENCRYPTION_KEY else Fernet.generate_key()
    return Fernet(key)


def encrypt(value: str) -> str:
    return _get_fernet().encrypt(value.encode()).decode()


def decrypt(value: str) -> str:
    return _get_fernet().decrypt(value.encode()).decode()


def generate_key() -> str:
    return Fernet.generate_key().decode()
