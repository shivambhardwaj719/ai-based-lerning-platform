"""AuditService — writes sensitive actions to the audit_logs table."""
from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

log = structlog.get_logger()

SENSITIVE_ACTIONS = frozenset({
    "login",
    "login_failed",
    "logout",
    "register",
    "password_change",
    "password_reset",
    "2fa_enable",
    "2fa_disable",
    "2fa_verify",
    "oauth_link",
    "oauth_unlink",
    "session_revoke",
    "role_change",
    "permission_grant",
    "permission_revoke",
    "admin_action",
    "payment",
    "subscription_change",
    "data_export",
    "account_delete",
    "api_key_create",
    "api_key_revoke",
})


class AuditService:
    """Persist audit events to the database and emit structured logs."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def log(
        self,
        action: str,
        user_id: uuid.UUID | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        resource_type: str | None = None,
        resource_id: str | None = None,
        success: bool = True,
        failure_reason: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Write an audit record to the DB and emit a structured log line."""
        from sqlalchemy import text

        record_id = uuid.uuid4()
        now = datetime.now(UTC)

        try:
            await self.db.execute(
                text("""
                    INSERT INTO audit_logs
                        (id, user_id, action, ip_address, user_agent,
                         resource_type, resource_id, success, failure_reason,
                         metadata, created_at)
                    VALUES
                        (:id, :user_id, :action, :ip_address, :user_agent,
                         :resource_type, :resource_id, :success, :failure_reason,
                         :metadata::jsonb, :created_at)
                """),
                {
                    "id": record_id,
                    "user_id": user_id,
                    "action": action,
                    "ip_address": ip_address,
                    "user_agent": user_agent,
                    "resource_type": resource_type,
                    "resource_id": str(resource_id) if resource_id else None,
                    "success": success,
                    "failure_reason": failure_reason,
                    "metadata": str(metadata or {}),
                    "created_at": now,
                },
            )
        except Exception as exc:
            # Audit logging must never crash the main request
            log.error("audit_log_db_error", error=str(exc), action=action)

        log.info(
            "audit",
            audit_id=str(record_id),
            action=action,
            user_id=str(user_id) if user_id else None,
            ip_address=ip_address,
            success=success,
            failure_reason=failure_reason,
        )

    async def log_login(
        self, user_id: uuid.UUID, ip: str, user_agent: str, success: bool,
        failure_reason: str | None = None,
    ) -> None:
        await self.log(
            action="login" if success else "login_failed",
            user_id=user_id,
            ip_address=ip,
            user_agent=user_agent,
            success=success,
            failure_reason=failure_reason,
        )

    async def log_admin_action(
        self, admin_id: uuid.UUID, action: str, target_user_id: uuid.UUID | None,
        details: dict[str, Any] | None = None,
    ) -> None:
        await self.log(
            action=f"admin:{action}",
            user_id=admin_id,
            resource_type="user",
            resource_id=str(target_user_id) if target_user_id else None,
            metadata=details,
        )
