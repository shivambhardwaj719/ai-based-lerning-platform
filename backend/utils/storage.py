"""S3-compatible object storage utilities."""
from __future__ import annotations

import uuid
from pathlib import Path

import aioboto3
import structlog
from fastapi import UploadFile

from core.config import settings

log = structlog.get_logger()
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_AVATAR_SIZE = 5 * 1024 * 1024  # 5MB


async def upload_file(file: UploadFile, folder: str = "uploads") -> str:
    content = await file.read()
    ext = Path(file.filename or "file").suffix
    key = f"{folder}/{uuid.uuid4()}{ext}"

    session = aioboto3.Session()
    async with session.client(
        "s3",
        endpoint_url=f"https://s3.{settings.AWS_REGION}.amazonaws.com",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    ) as s3:
        await s3.put_object(
            Bucket=settings.AWS_S3_BUCKET,
            Key=key,
            Body=content,
            ContentType=file.content_type or "application/octet-stream",
            ACL="public-read",
        )

    cdn = settings.CDN_URL or f"https://{settings.AWS_S3_BUCKET}.s3.{settings.AWS_REGION}.amazonaws.com"
    return f"{cdn}/{key}"
