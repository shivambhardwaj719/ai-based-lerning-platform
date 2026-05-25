"""
AI Roadmap Generator: creates personalized learning roadmaps using LangGraph.
Generates skill trees, milestone timelines, and resource recommendations.
"""
from __future__ import annotations

import json
import uuid
from typing import Any, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings


ROADMAP_SYSTEM_PROMPT = """You are an expert technical learning roadmap generator.
Create detailed, personalized learning roadmaps based on the user's goals and current skills.

Generate a roadmap with:
1. Clear milestones and weekly breakdowns
2. Specific resources (books, courses, projects)
3. Hands-on projects for each stage
4. Skills dependencies and prerequisites
5. Estimated time for each topic

Return a JSON object with this structure:
{
  "title": "...",
  "description": "...",
  "total_weeks": N,
  "nodes": [
    {
      "id": "node_1",
      "title": "...",
      "description": "...",
      "type": "topic|project|milestone",
      "week": N,
      "duration_hours": N,
      "resources": [...],
      "skills": [...],
      "dependencies": [...]
    }
  ],
  "edges": [
    {"from": "node_1", "to": "node_2", "type": "prerequisite"}
  ]
}"""


class RoadmapState(TypedDict):
    messages: list
    goal: str
    target_role: str | None
    current_skills: list[str]
    experience_level: str
    available_hours_per_week: int
    timeline_weeks: int | None
    generated_roadmap: dict | None


class RoadmapAgent:
    def __init__(self, user_id: uuid.UUID, db: AsyncSession) -> None:
        self.user_id = user_id
        self.db = db
        self.llm = ChatOpenAI(
            model="gpt-4o",
            api_key=settings.OPENAI_API_KEY,
            temperature=0.3,
            response_format={"type": "json_object"},
        )
        self._graph = self._build_graph()

    def _build_graph(self) -> Any:
        async def generate_roadmap(state: RoadmapState) -> RoadmapState:
            user_msg = f"""
Create a learning roadmap:
- Goal: {state['goal']}
- Target Role: {state.get('target_role', 'Not specified')}
- Current Skills: {', '.join(state['current_skills']) or 'None'}
- Experience Level: {state['experience_level']}
- Available: {state['available_hours_per_week']} hours/week
- Timeline: {state.get('timeline_weeks', 'Flexible')} weeks
"""
            messages = [
                SystemMessage(content=ROADMAP_SYSTEM_PROMPT),
                HumanMessage(content=user_msg),
            ]
            response = await self.llm.ainvoke(messages)
            roadmap_data = json.loads(response.content)
            return {**state, "generated_roadmap": roadmap_data}

        async def save_roadmap(state: RoadmapState) -> RoadmapState:
            if state.get("generated_roadmap"):
                data = state["generated_roadmap"]
                from repositories.ai_repository import RoadmapRepository
                repo = RoadmapRepository(self.db)
                await repo.create(
                    user_id=self.user_id,
                    title=data.get("title", "My Learning Roadmap"),
                    description=data.get("description"),
                    goal=state["goal"],
                    target_role=state.get("target_role"),
                    estimated_weeks=data.get("total_weeks"),
                    nodes=data.get("nodes"),
                    edges=data.get("edges"),
                    is_ai_generated=True,
                )
            return state

        workflow = StateGraph(RoadmapState)
        workflow.add_node("generate", generate_roadmap)
        workflow.add_node("save", save_roadmap)
        workflow.set_entry_point("generate")
        workflow.add_edge("generate", "save")
        workflow.add_edge("save", END)
        return workflow.compile()

    async def generate(
        self,
        goal: str,
        target_role: str | None = None,
        current_skills: list[str] | None = None,
        experience_level: str = "beginner",
        available_hours_per_week: int = 10,
        timeline_weeks: int | None = None,
    ) -> Any:
        state = RoadmapState(
            messages=[],
            goal=goal,
            target_role=target_role,
            current_skills=current_skills or [],
            experience_level=experience_level,
            available_hours_per_week=available_hours_per_week,
            timeline_weeks=timeline_weeks,
            generated_roadmap=None,
        )
        final = await self._graph.ainvoke(state)
        return final.get("generated_roadmap")
