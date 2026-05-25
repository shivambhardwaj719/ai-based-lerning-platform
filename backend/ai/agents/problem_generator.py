"""AI Problem Generator: creates coding problems with test cases."""
from __future__ import annotations

import json

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings


PROBLEM_GEN_SYSTEM = """You are an expert competitive programming problem setter.
Create original, high-quality coding problems.

Return JSON array of problems:
[{
  "title": "...",
  "description": "...",
  "difficulty": "easy|medium|hard|expert",
  "problem_type": "algorithmic|data_structure|...",
  "tags": [...],
  "constraints": "...",
  "examples": [{"input": "...", "output": "...", "explanation": "..."}],
  "test_cases": [{"input": "...", "expected_output": "...", "is_sample": true}],
  "time_limit_ms": 2000,
  "memory_limit_mb": 256,
  "hints": ["..."],
  "editorial": "..."
}]"""


class ProblemGeneratorAgent:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.llm = ChatOpenAI(
            model="gpt-4o",
            api_key=settings.OPENAI_API_KEY,
            temperature=0.8,
            response_format={"type": "json_object"},
        )

    async def generate(
        self,
        topic: str,
        difficulty: str = "medium",
        problem_type: str = "algorithmic",
        tags: list[str] | None = None,
        count: int = 1,
    ) -> list[dict]:
        prompt = f"""Generate {count} original {difficulty} {problem_type} problem(s) on topic: {topic}.
Tags: {', '.join(tags or [])}
Make problems unique, educational, and well-tested."""

        messages = [SystemMessage(content=PROBLEM_GEN_SYSTEM), HumanMessage(content=prompt)]
        response = await self.llm.ainvoke(messages)
        data = json.loads(response.content)
        problems = data if isinstance(data, list) else data.get("problems", [])

        # Persist to database
        saved_problems = []
        for p in problems[:count]:
            saved = await self._save_problem(p)
            saved_problems.append(saved)

        return saved_problems

    async def _save_problem(self, data: dict) -> dict:
        from repositories.problem_repository import ProblemRepository
        from python_slugify import slugify
        import uuid as uuid_mod

        repo = ProblemRepository(self.db)
        slug = slugify(data["title"]) + "-" + str(uuid_mod.uuid4())[:8]

        test_cases = data.pop("test_cases", [])
        problem = await repo.create(
            title=data["title"],
            slug=slug,
            description=data["description"],
            difficulty=data.get("difficulty", "medium"),
            problem_type=data.get("problem_type", "algorithmic"),
            tags=data.get("tags"),
            constraints=data.get("constraints"),
            examples=data.get("examples"),
            hints=data.get("hints"),
            editorial=data.get("editorial"),
            time_limit_ms=data.get("time_limit_ms", 2000),
            memory_limit_mb=data.get("memory_limit_mb", 256),
            is_ai_generated=True,
            is_published=False,
        )

        from models.problem import TestCase
        from repositories.base import BaseRepository
        tc_repo = BaseRepository(TestCase, self.db)
        for tc in test_cases:
            await tc_repo.create(
                problem_id=problem.id,
                input_data=tc.get("input", ""),
                expected_output=tc.get("expected_output", ""),
                is_sample=tc.get("is_sample", False),
            )

        return {"id": str(problem.id), "title": problem.title, "slug": problem.slug}
