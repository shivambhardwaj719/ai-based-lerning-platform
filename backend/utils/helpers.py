"""Common utility helpers used across the application."""
from __future__ import annotations

import hashlib
import re
import secrets
import string
import uuid
from datetime import UTC, datetime
from typing import Any


def generate_random_string(length: int = 32, alphabet: str | None = None) -> str:
    """Generate a cryptographically secure random string."""
    chars = alphabet or (string.ascii_letters + string.digits)
    return "".join(secrets.choice(chars) for _ in range(length))


def slugify(text: str) -> str:
    """Convert a string to a URL-safe slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text


def hash_string(value: str, algorithm: str = "sha256") -> str:
    """Return hex digest of a string using the given hash algorithm."""
    return hashlib.new(algorithm, value.encode()).hexdigest()


def mask_email(email: str) -> str:
    """Partially mask an email for display (e.g. 'jo***@example.com')."""
    parts = email.split("@")
    if len(parts) != 2:
        return email
    user, domain = parts
    visible = max(2, len(user) // 3)
    return f"{user[:visible]}{'*' * (len(user) - visible)}@{domain}"


def paginate(items: list[Any], page: int, per_page: int) -> tuple[list[Any], int]:
    """Slice a list for pagination, return (page_items, total)."""
    total = len(items)
    start = (page - 1) * per_page
    return items[start : start + per_page], total


def safe_uuid(value: str) -> uuid.UUID | None:
    """Parse a UUID string, returning None if invalid."""
    try:
        return uuid.UUID(value)
    except (ValueError, AttributeError):
        return None


def utc_now() -> datetime:
    """Return current UTC datetime (timezone-aware)."""
    return datetime.now(UTC)


def truncate(text: str, max_length: int = 200, suffix: str = "…") -> str:
    """Truncate text to max_length, appending suffix if truncated."""
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def flatten(nested: list[list[Any]]) -> list[Any]:
    """Flatten one level of nesting."""
    return [item for sublist in nested for item in sublist]


def chunk(lst: list[Any], size: int) -> list[list[Any]]:
    """Split a list into chunks of given size."""
    return [lst[i : i + size] for i in range(0, len(lst), size)]


def normalize_language(lang: str) -> str:
    """Normalize language identifiers to canonical form."""
    mapping = {
        "py": "python",
        "python3": "python",
        "js": "javascript",
        "ts": "typescript",
        "cpp": "cpp",
        "c++": "cpp",
        "golang": "go",
        "rs": "rust",
        "kt": "kotlin",
    }
    return mapping.get(lang.lower(), lang.lower())
