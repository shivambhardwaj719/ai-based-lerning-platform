"""
Role-Based Access Control (RBAC) with hierarchical permissions.
"""
from __future__ import annotations

from enum import Enum
from functools import wraps
from typing import Any, Callable

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.exceptions import InsufficientPermissionsError
from models.user import UserRole


class Permission(str, Enum):
    # User permissions
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    USER_MANAGE = "user:manage"

    # Problem permissions
    PROBLEM_READ = "problem:read"
    PROBLEM_CREATE = "problem:create"
    PROBLEM_UPDATE = "problem:update"
    PROBLEM_DELETE = "problem:delete"
    PROBLEM_PUBLISH = "problem:publish"

    # Submission permissions
    SUBMISSION_CREATE = "submission:create"
    SUBMISSION_READ = "submission:read"
    SUBMISSION_READ_ALL = "submission:read_all"

    # Contest permissions
    CONTEST_READ = "contest:read"
    CONTEST_CREATE = "contest:create"
    CONTEST_MANAGE = "contest:manage"
    CONTEST_PARTICIPATE = "contest:participate"

    # AI permissions
    AI_CHAT = "ai:chat"
    AI_GENERATE = "ai:generate"
    AI_MENTOR = "ai:mentor"

    # Lab permissions
    LAB_ACCESS = "lab:access"
    LAB_CREATE = "lab:create"
    LAB_MANAGE = "lab:manage"

    # Admin permissions
    ADMIN_PANEL = "admin:panel"
    ADMIN_USERS = "admin:users"
    ADMIN_CONTENT = "admin:content"
    ADMIN_ANALYTICS = "admin:analytics"
    ADMIN_SYSTEM = "admin:system"

    # Payment permissions
    PAYMENT_CREATE = "payment:create"
    PAYMENT_READ = "payment:read"
    PAYMENT_MANAGE = "payment:manage"


# Role → Set of permissions
ROLE_PERMISSIONS: dict[UserRole, set[Permission]] = {
    UserRole.STUDENT: {
        Permission.USER_READ,
        Permission.USER_UPDATE,
        Permission.PROBLEM_READ,
        Permission.SUBMISSION_CREATE,
        Permission.SUBMISSION_READ,
        Permission.CONTEST_READ,
        Permission.CONTEST_PARTICIPATE,
        Permission.AI_CHAT,
        Permission.AI_MENTOR,
        Permission.LAB_ACCESS,
        Permission.PAYMENT_CREATE,
        Permission.PAYMENT_READ,
    },
    UserRole.INSTRUCTOR: {
        Permission.USER_READ,
        Permission.USER_UPDATE,
        Permission.PROBLEM_READ,
        Permission.PROBLEM_CREATE,
        Permission.PROBLEM_UPDATE,
        Permission.PROBLEM_PUBLISH,
        Permission.SUBMISSION_CREATE,
        Permission.SUBMISSION_READ,
        Permission.SUBMISSION_READ_ALL,
        Permission.CONTEST_READ,
        Permission.CONTEST_CREATE,
        Permission.CONTEST_MANAGE,
        Permission.CONTEST_PARTICIPATE,
        Permission.AI_CHAT,
        Permission.AI_GENERATE,
        Permission.AI_MENTOR,
        Permission.LAB_ACCESS,
        Permission.LAB_CREATE,
        Permission.PAYMENT_CREATE,
        Permission.PAYMENT_READ,
    },
    UserRole.MENTOR: {
        Permission.USER_READ,
        Permission.USER_UPDATE,
        Permission.PROBLEM_READ,
        Permission.SUBMISSION_READ,
        Permission.SUBMISSION_READ_ALL,
        Permission.CONTEST_READ,
        Permission.AI_CHAT,
        Permission.AI_MENTOR,
        Permission.LAB_ACCESS,
        Permission.PAYMENT_CREATE,
        Permission.PAYMENT_READ,
    },
    UserRole.ADMIN: {p for p in Permission},
    UserRole.SUPER_ADMIN: {p for p in Permission},
}


def has_permission(role: UserRole, permission: Permission) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, set())


def check_role(user_role: str, required_role: UserRole) -> None:
    role_hierarchy = [
        UserRole.STUDENT,
        UserRole.MENTOR,
        UserRole.INSTRUCTOR,
        UserRole.ADMIN,
        UserRole.SUPER_ADMIN,
    ]
    try:
        user_level = role_hierarchy.index(UserRole(user_role))
        required_level = role_hierarchy.index(required_role)
        if user_level < required_level:
            raise InsufficientPermissionsError(required_role=required_role.value)
    except ValueError:
        raise InsufficientPermissionsError()


# ── FastAPI dependencies ──────────────────────────────────────────────────────

def require_role(*roles: UserRole):
    """Dependency factory: require one of the specified roles."""
    from auth.dependencies import get_current_user

    async def _check(current_user=Depends(get_current_user)):
        if UserRole(current_user.role) not in roles:
            raise InsufficientPermissionsError()
        return current_user

    return _check


def require_permission(permission: Permission):
    """Dependency factory: require a specific permission."""
    from auth.dependencies import get_current_user

    async def _check(current_user=Depends(get_current_user)):
        if not has_permission(UserRole(current_user.role), permission):
            raise InsufficientPermissionsError()
        return current_user

    return _check
