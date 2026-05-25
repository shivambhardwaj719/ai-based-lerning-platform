"""AI Debugging Assistant: analyzes errors, suggests fixes."""
from __future__ import annotations

import json

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from core.config import settings


DEBUG_SYSTEM = """You are an expert debugging assistant.
Analyze code errors and provide clear explanations and fixes.

Return JSON:
{
  "error_type": "...",
  "explanation": "...",
  "root_cause": "...",
  "fix": "...",
  "fixed_code": "...",
  "prevention": "...",
  "related_concepts": [...]
}"""


class DebugAgent:
    def __init__(self) -> None:
        self.llm = ChatOpenAI(
            model=settings.DEFAULT_AI_MODEL,
            api_key=settings.OPENAI_API_KEY,
            temperature=0.1,
            response_format={"type": "json_object"},
        )

    async def debug(
        self,
        code: str,
        language: str,
        error: str,
        context: str | None = None,
    ) -> dict:
        prompt = f"""Debug this {language} code:

Error: {error}
{f'Context: {context}' if context else ''}

```{language}
{code}
```"""
        messages = [SystemMessage(content=DEBUG_SYSTEM), HumanMessage(content=prompt)]
        response = await self.llm.ainvoke(messages)
        return json.loads(response.content)
