"""Integration tests for Contest API endpoints."""
from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestContestList:
    async def test_list_contests_unauthenticated(self, client: AsyncClient):
        response = await client.get("/api/v1/contests/")
        assert response.status_code == 200
        data = response.json()
        assert "contests" in data
        assert "total" in data

    async def test_list_contests_pagination(self, client: AsyncClient):
        response = await client.get("/api/v1/contests/?page=1&per_page=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data["contests"]) <= 5


@pytest.mark.asyncio
class TestContestJoin:
    async def test_join_contest_requires_auth(self, client: AsyncClient, test_contest):
        response = await client.post(f"/api/v1/contests/{test_contest['id']}/join")
        assert response.status_code == 401

    async def test_join_active_contest(self, client: AsyncClient, auth_headers, test_contest):
        response = await client.post(
            f"/api/v1/contests/{test_contest['id']}/join",
            headers=auth_headers,
        )
        # Either 200 (joined) or 409 (already joined)
        assert response.status_code in (200, 409)

    async def test_join_nonexistent_contest_404(self, client: AsyncClient, auth_headers):
        import uuid
        fake_id = uuid.uuid4()
        response = await client.post(
            f"/api/v1/contests/{fake_id}/join",
            headers=auth_headers,
        )
        assert response.status_code == 404


@pytest.mark.asyncio
class TestContestLeaderboard:
    async def test_get_leaderboard(self, client: AsyncClient, test_contest):
        response = await client.get(f"/api/v1/contests/{test_contest['id']}/leaderboard")
        assert response.status_code == 200
        data = response.json()
        assert "entries" in data
        assert "contest_id" in data
