"""
FastAPI auth dependencies: current user extraction, optional auth, admin guards.
"""
from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import Depends, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession

from auth.jwt import TokenType, get_token_from_header, verify_access_token
from core.database import get_db
from core.exceptions import AuthenticationError, EmailNotVerifiedError, InsufficientPermissionsError
from models.user import User, UserRole, UserStatus
from repositories.user_repository import UserRepository


async def get_current_user_optional(
    authorization: Annotated[str | None, Header()] = None,
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """Extract current user if token provided; return None otherwise."""
    token = get_token_from_header(authorization)
    if not token:
        return None
    try:
        payload = await verify_access_token(token)
        user_id = uuid.UUID(payload["sub"])
        repo = UserRepository(db)
        return await repo.get_by_id(user_id)
    except Exception:
        return None


async def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
    db: AsyncSession = Depends(get_db),
) -> User:
    """Require authenticated user or raise 401."""
    token = get_token_from_header(authorization)
    if not token:
        raise AuthenticationError()

    payload = await verify_access_token(token)
    user_id = uuid.UUID(payload["sub"])

    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    if not user:
        raise AuthenticationError("User not found")

    if user.status == UserStatus.SUSPENDED:
        raise AuthenticationError("Account is suspended")

    if user.status == UserStatus.DELETED:
        raise AuthenticationError("Account has been deleted")

    return user


async def get_verified_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Require email-verified user."""
    if not current_user.is_email_verified:
        raise EmailNotVerifiedError()
    return current_user


async def get_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Require admin or super_admin role."""
    if current_user.role not in (UserRole.ADMIN, UserRole.SUPER_ADMIN):
        raise InsufficientPermissionsError(required_role="admin")
    return current_user


async def get_super_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != UserRole.SUPER_ADMIN:
        raise InsufficientPermissionsError(required_role="super_admin")
    return current_user


# Type aliases for cleaner route signatures
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentUserOptional = Annotated[User | None, Depends(get_current_user_optional)]
VerifiedUser = Annotated[User, Depends(get_verified_user)]
AdminUser = Annotated[User, Depends(get_admin_user)]
SuperAdmin = Annotated[User, Depends(get_super_admin)]
