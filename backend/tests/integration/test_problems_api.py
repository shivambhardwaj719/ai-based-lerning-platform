"""Integration tests for problems API."""
from __future__ import annotations

import uuid
import pytest
from httpx import AsyncClient


@pytest.fixture
async def test_problem(db_session):
    from repositories.problem_repository import ProblemRepository
    repo = ProblemRepository(db_session)
    return await repo.create(
        title="Two Sum",
        slug="two-sum",
        description="Given an array of integers, return indices of the two numbers that add up to a target.",
        difficulty="easy",
        problem_type="algorithmic",
        tags=["array", "hash-table"],
        time_limit_ms=2000,
        memory_limit_mb=256,
        is_published=True,
        examples=[{"input": "[2,7,11,15]\n9", "output": "[0,1]", "explanation": "2+7=9"}],
    )


@pytest.mark.asyncio
class TestProblems:
    async def test_list_problems(self, client: AsyncClient, test_problem):
        response = await client.get("/api/v1/problems")
        assert response.status_code == 200
        data = response.json()
        assert "problems" in data
        assert data["total"] >= 1

    async def test_get_problem_by_slug(self, client: AsyncClient, test_problem):
        response = await client.get(f"/api/v1/problems/{test_problem.slug}")
        assert response.status_code == 200
        data = response.json()
        assert data["slug"] == test_problem.slug
        assert data["title"] == test_problem.title

    async def test_get_nonexistent_problem(self, client: AsyncClient):
        response = await client.get("/api/v1/problems/nonexistent-slug")
        assert response.status_code == 404

    async def test_submit_requires_auth(self, client: AsyncClient, test_problem):
        response = await client.post("/api/v1/problems/submit", json={
            "problem_id": str(test_problem.id),
            "code": "print('hello')",
            "language": "python",
        })
        assert response.status_code == 401

    async def test_filter_by_difficulty(self, client: AsyncClient, test_problem):
        response = await client.get("/api/v1/problems?difficulty=easy")
        assert response.status_code == 200
        data = response.json()
        assert all(p["difficulty"] == "easy" for p in data["problems"])
