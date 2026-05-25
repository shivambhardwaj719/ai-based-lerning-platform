"""Unit tests for RBAC dependency factories."""
from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock


class TestRequireRole:
    @pytest.mark.asyncio
    async def test_sufficient_role_passes(self):
        from auth.rbac import UserRole, require_role
        from core.exceptions import AuthorizationError

        user = MagicMock()
        user.role = UserRole.ADMIN

        dep = require_role(UserRole.INSTRUCTOR)
        # Should not raise
        result = await dep(current_user=user)
        assert result == user

    @pytest.mark.asyncio
    async def test_insufficient_role_raises(self):
        from auth.rbac import UserRole, require_role
        from core.exceptions import AuthorizationError

        user = MagicMock()
        user.role = UserRole.STUDENT

        dep = require_role(UserRole.INSTRUCTOR)
        with pytest.raises(AuthorizationError):
            await dep(current_user=user)


class TestRequirePermission:
    @pytest.mark.asyncio
    async def test_user_with_permission_passes(self):
        from auth.rbac import ROLE_PERMISSIONS, Permission, UserRole, require_permission

        user = MagicMock()
        user.role = UserRole.ADMIN

        dep = require_permission(Permission.MANAGE_USERS)
        result = await dep(current_user=user)
        assert result == user

    @pytest.mark.asyncio
    async def test_user_without_permission_raises(self):
        from auth.rbac import Permission, UserRole, require_permission
        from core.exceptions import AuthorizationError

        user = MagicMock()
        user.role = UserRole.STUDENT

        dep = require_permission(Permission.MANAGE_USERS)
        with pytest.raises(AuthorizationError):
            await dep(current_user=user)
