"""User, Session, and OAuthAccount repository."""
from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import and_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.user import AuditLog, OAuthAccount, Session, User, UserProfile
from repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> User | None:
        stmt = (
            select(User)
            .where(User.email == email.lower())
            .options(selectinload(User.profile))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_with_profile(self, user_id: uuid.UUID) -> User | None:
        stmt = (
            select(User)
            .where(User.id == user_id)
            .options(
                selectinload(User.profile),
                selectinload(User.oauth_accounts),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def email_exists(self, email: str) -> bool:
        return await self.get_by_email(email) is not None

    async def username_exists(self, username: str) -> bool:
        return await self.get_by_username(username) is not None

    async def increment_login_attempts(self, user_id: uuid.UUID) -> int:
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(login_attempts=User.login_attempts + 1)
            .returning(User.login_attempts)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def reset_login_attempts(self, user_id: uuid.UUID) -> None:
        await self.update(user_id, login_attempts=0, locked_until=None)

    async def update_last_login(self, user_id: uuid.UUID, ip_address: str) -> None:
        await self.update(
            user_id,
            last_login_at=datetime.now(UTC),
            last_login_ip=ip_address,
            login_attempts=0,
            locked_until=None,
        )


class SessionRepository(BaseRepository[Session]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Session, db)

    async def get_by_refresh_token_hash(self, token_hash: str) -> Session | None:
        return await self.get_by_field("refresh_token_hash", token_hash)

    async def get_active_sessions(self, user_id: uuid.UUID) -> list[Session]:
        stmt = select(Session).where(
            and_(
                Session.user_id == user_id,
                Session.is_active == True,
                Session.expires_at > datetime.now(UTC),
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def revoke_all_sessions(self, user_id: uuid.UUID) -> None:
        stmt = (
            update(Session)
            .where(and_(Session.user_id == user_id, Session.is_active == True))
            .values(is_active=False)
        )
        await self.session.execute(stmt)

    async def revoke_session(self, session_id: uuid.UUID) -> None:
        await self.update(session_id, is_active=False)

    async def touch_session(self, session_id: uuid.UUID) -> None:
        await self.update(session_id, last_used_at=datetime.now(UTC))


class OAuthAccountRepository(BaseRepository[OAuthAccount]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(OAuthAccount, db)

    async def get_by_provider(self, provider: str, provider_user_id: str) -> OAuthAccount | None:
        stmt = select(OAuthAccount).where(
            and_(
                OAuthAccount.provider == provider,
                OAuthAccount.provider_user_id == provider_user_id,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_providers(self, user_id: uuid.UUID) -> list[OAuthAccount]:
        stmt = select(OAuthAccount).where(OAuthAccount.user_id == user_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class AuditLogRepository(BaseRepository[AuditLog]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(AuditLog, db)

    async def log_action(
        self,
        action: str,
        user_id: uuid.UUID | None = None,
        resource_type: str | None = None,
        resource_id: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        request_id: str | None = None,
        metadata: dict | None = None,
        success: bool = True,
        error_message: str | None = None,
    ) -> AuditLog:
        return await self.create(
            action=action,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id,
            metadata_=metadata,
            success=success,
            error_message=error_message,
        )
