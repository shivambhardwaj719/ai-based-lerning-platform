"""Integration tests for auth API endpoints."""
from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestRegister:
    async def test_register_success(self, client: AsyncClient):
        response = await client.post("/api/v1/auth/register", json={
            "email": "newuser@example.com",
            "username": "newuser123",
            "password": "NewPass123!",
            "full_name": "New User",
        })
        assert response.status_code == 201
        data = response.json()
        assert "user_id" in data

    async def test_register_duplicate_email(self, client: AsyncClient, test_user):
        response = await client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "username": "different_username",
            "password": "NewPass123!",
            "full_name": "Another User",
        })
        assert response.status_code == 409

    async def test_register_weak_password(self, client: AsyncClient):
        response = await client.post("/api/v1/auth/register", json={
            "email": "weak@example.com",
            "username": "weakuser",
            "password": "weak",
            "full_name": "Weak User",
        })
        assert response.status_code == 422

    async def test_register_invalid_username(self, client: AsyncClient):
        response = await client.post("/api/v1/auth/register", json={
            "email": "valid@example.com",
            "username": "user with spaces",
            "password": "ValidPass123!",
            "full_name": "Test User",
        })
        assert response.status_code == 422


@pytest.mark.asyncio
class TestLogin:
    async def test_login_success(self, client: AsyncClient, test_user):
        response = await client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "TestPass123!",
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "Bearer"

    async def test_login_wrong_password(self, client: AsyncClient, test_user):
        response = await client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "WrongPassword123!",
        })
        assert response.status_code == 401

    async def test_login_nonexistent_email(self, client: AsyncClient):
        response = await client.post("/api/v1/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "SomePass123!",
        })
        assert response.status_code == 401


@pytest.mark.asyncio
class TestProtectedEndpoints:
    async def test_get_me_authenticated(self, client: AsyncClient, auth_headers):
        response = await client.get("/api/v1/users/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"

    async def test_get_me_unauthenticated(self, client: AsyncClient):
        response = await client.get("/api/v1/users/me")
        assert response.status_code == 401

    async def test_get_me_invalid_token(self, client: AsyncClient):
        response = await client.get("/api/v1/users/me",
                                    headers={"Authorization": "Bearer invalid.token.here"})
        assert response.status_code == 401


@pytest.mark.asyncio
class TestTokenRefresh:
    async def test_refresh_token(self, client: AsyncClient, test_user):
        login_resp = await client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "TestPass123!",
        })
        refresh_token = login_resp.json()["refresh_token"]

        refresh_resp = await client.post("/api/v1/auth/refresh", json={
            "refresh_token": refresh_token,
        })
        assert refresh_resp.status_code == 200
        assert "access_token" in refresh_resp.json()

    async def test_invalid_refresh_token(self, client: AsyncClient):
        response = await client.post("/api/v1/auth/refresh", json={
            "refresh_token": "invalid_refresh_token",
        })
        assert response.status_code == 401
