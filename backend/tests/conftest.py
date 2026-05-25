"""
Pytest configuration and shared fixtures.
"""
from __future__ import annotations

import asyncio
import uuid
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from core.config import settings
from core.database import Base, database_manager, get_db
from main import app
from models import *  # noqa: register all models


TEST_DATABASE_URL = "postgresql+asyncpg://postgres:password@localhost:5432/ai_learning_test"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def db_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    session_factory = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        async with session.begin():
            yield session
            await session.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    app.dependency_overrides[get_db] = lambda: db_session
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession):
    from auth.password import hash_password
    from repositories.user_repository import UserRepository
    from models.user import UserStatus, UserRole
    from models.user import UserProfile
    from repositories.base import BaseRepository

    repo = UserRepository(db_session)
    user = await repo.create(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        hashed_password=hash_password("TestPass123!"),
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
        is_email_verified=True,
    )
    profile_repo = BaseRepository(UserProfile, db_session)
    await profile_repo.create(user_id=user.id)
    return user


@pytest_asyncio.fixture
async def auth_headers(test_user, client: AsyncClient) -> dict:
    response = await client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "TestPass123!",
    })
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession):
    from auth.password import hash_password
    from repositories.user_repository import UserRepository
    from models.user import UserStatus, UserRole

    repo = UserRepository(db_session)
    return await repo.create(
        email="admin@example.com",
        username="adminuser",
        full_name="Admin User",
        hashed_password=hash_password("AdminPass123!"),
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE,
        is_email_verified=True,
    )
