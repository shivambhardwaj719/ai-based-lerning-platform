"""AI Code Review Agent: analyzes code quality, bugs, and improvements."""
from __future__ import annotations

import json

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from core.config import settings


CODE_REVIEW_SYSTEM = """You are an expert code reviewer. Analyze code for:
1. Correctness and bugs
2. Time/space complexity
3. Code quality and readability
4. Security vulnerabilities
5. Best practices and design patterns

Return JSON with:
{
  "overall_score": 0-100,
  "feedback": "...",
  "issues": [{"type": "bug|style|security|performance", "line": N, "message": "..."}],
  "suggestions": ["..."],
  "optimizations": [{"description": "...", "impact": "high|medium|low"}],
  "best_practices": ["..."],
  "time_complexity": "O(...)",
  "space_complexity": "O(...)"
}"""


class CodeReviewAgent:
    def __init__(self) -> None:
        self.llm = ChatOpenAI(
            model="gpt-4o",
            api_key=settings.OPENAI_API_KEY,
            temperature=0.1,
            response_format={"type": "json_object"},
        )

    async def review(
        self,
        code: str,
        language: str,
        problem_context: str | None = None,
        focus_areas: list[str] | None = None,
    ) -> dict:
        focus = f"Focus on: {', '.join(focus_areas)}" if focus_areas else ""
        context = f"Problem context: {problem_context}" if problem_context else ""

        prompt = f"""
Review this {language} code:
{context}
{focus}

```{language}
{code}
```
"""
        messages = [SystemMessage(content=CODE_REVIEW_SYSTEM), HumanMessage(content=prompt)]
        response = await self.llm.ainvoke(messages)
        return json.loads(response.content)
