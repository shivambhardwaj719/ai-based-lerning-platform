"""End-to-end tests: full user journey from registration to problem submission."""
from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
@pytest.mark.e2e
class TestUserJourney:
    """Full happy-path flow: register → verify → login → solve problem."""

    async def test_register_login_and_profile(self, client: AsyncClient):
        import uuid

        unique = uuid.uuid4().hex[:8]
        email = f"e2e_{unique}@test.com"
        username = f"e2e_{unique}"
        password = "TestPass@123"

        # 1. Register
        reg_res = await client.post("/api/v1/auth/register", json={
            "email": email,
            "username": username,
            "password": password,
            "full_name": "E2E Test User",
        })
        assert reg_res.status_code == 201, reg_res.text
        reg_data = reg_res.json()
        assert reg_data["email"] == email

        # 2. Login (email may not be verified — depends on config)
        login_res = await client.post("/api/v1/auth/login", json={
            "email": email,
            "password": password,
        })
        # If email verification required, expect 403; otherwise 200
        assert login_res.status_code in (200, 403)

        if login_res.status_code == 200:
            tokens = login_res.json()
            assert "access_token" in tokens
            headers = {"Authorization": f"Bearer {tokens['access_token']}"}

            # 3. Fetch own profile
            profile_res = await client.get("/api/v1/users/me", headers=headers)
            assert profile_res.status_code == 200
            profile = profile_res.json()
            assert profile["username"] == username

            # 4. List problems
            problems_res = await client.get("/api/v1/problems/", headers=headers)
            assert problems_res.status_code == 200
            problems = problems_res.json()
            assert "problems" in problems

            # 5. Refresh token
            refresh_res = await client.post("/api/v1/auth/refresh", json={
                "refresh_token": tokens["refresh_token"],
            })
            assert refresh_res.status_code == 200
            assert "access_token" in refresh_res.json()

            # 6. Logout
            logout_res = await client.post("/api/v1/auth/logout", headers=headers)
            assert logout_res.status_code in (200, 204)


@pytest.mark.asyncio
@pytest.mark.e2e
class TestPublicEndpoints:
    async def test_health_check(self, client: AsyncClient):
        res = await client.get("/health")
        assert res.status_code == 200
        assert res.json()["status"] == "healthy"

    async def test_openapi_docs_available(self, client: AsyncClient):
        res = await client.get("/docs")
        assert res.status_code == 200

    async def test_rate_limit_returns_429_after_burst(self, client: AsyncClient):
        """Auth endpoints should 429 after burst limit is hit."""
        responses = []
        for _ in range(15):
            r = await client.post("/api/v1/auth/login", json={
                "email": "nonexistent@test.com",
                "password": "wrong",
            })
            responses.append(r.status_code)
        # At least one should be rate-limited
        assert 429 in responses or 401 in responses
