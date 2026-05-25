"""Integration tests for AI API endpoints."""
from __future__ import annotations

import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
class TestAIChat:
    async def test_chat_requires_auth(self, client: AsyncClient):
        response = await client.post("/api/v1/ai/chat", json={"message": "Hello"})
        assert response.status_code == 401

    async def test_chat_empty_message_rejected(self, client: AsyncClient, auth_headers):
        response = await client.post(
            "/api/v1/ai/chat",
            json={"message": ""},
            headers=auth_headers,
        )
        assert response.status_code == 422

    async def test_chat_non_streaming(self, client: AsyncClient, auth_headers):
        with patch("ai.agents.mentor_agent.MentorAgent.chat") as mock_chat:
            mock_chat.return_value = {"response": "Hello! How can I help you today?"}
            response = await client.post(
                "/api/v1/ai/chat",
                json={"message": "What is binary search?", "streaming": False},
                headers=auth_headers,
            )
        assert response.status_code == 200

    async def test_chat_message_length_limit(self, client: AsyncClient, auth_headers):
        long_message = "x" * 10001
        response = await client.post(
            "/api/v1/ai/chat",
            json={"message": long_message},
            headers=auth_headers,
        )
        assert response.status_code == 422


@pytest.mark.asyncio
class TestRoadmap:
    async def test_generate_roadmap_requires_auth(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/ai/roadmap/generate",
            json={"goal": "Learn DSA"},
        )
        assert response.status_code == 401

    async def test_generate_roadmap(self, client: AsyncClient, auth_headers):
        with patch("ai.agents.roadmap_agent.RoadmapAgent.generate") as mock_gen:
            mock_gen.return_value = {
                "title": "DSA Roadmap",
                "nodes": [{"id": "1", "label": "Arrays", "completed": False}],
                "edges": [],
            }
            response = await client.post(
                "/api/v1/ai/roadmap/generate",
                json={"goal": "Master data structures", "experience_level": "beginner"},
                headers=auth_headers,
            )
        assert response.status_code in (200, 201)


@pytest.mark.asyncio
class TestCodeReview:
    async def test_code_review_requires_auth(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/ai/code-review",
            json={"code": "print('hello')", "language": "python"},
        )
        assert response.status_code == 401

    async def test_code_review_missing_language(self, client: AsyncClient, auth_headers):
        response = await client.post(
            "/api/v1/ai/code-review",
            json={"code": "print('hello')"},
            headers=auth_headers,
        )
        assert response.status_code == 422
