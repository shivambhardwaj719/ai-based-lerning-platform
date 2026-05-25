"""AI Interview System: conducts mock technical interviews."""
from __future__ import annotations

import json
import uuid
from typing import TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.redis import redis_manager


INTERVIEWER_SYSTEM = """You are a senior technical interviewer at a top tech company.
Conduct professional technical interviews. Ask questions progressively.
Evaluate answers for correctness, depth, communication, and problem-solving approach."""


class InterviewState(TypedDict):
    messages: list
    interview_type: str
    role: str
    experience_level: str
    topics: list[str]
    current_question_index: int
    questions: list[dict]
    answers: list[dict]
    session_id: str


class InterviewAgent:
    def __init__(self, user_id: uuid.UUID, db: AsyncSession | None = None) -> None:
        self.user_id = user_id
        self.db = db
        self.llm = ChatOpenAI(
            model="gpt-4o",
            api_key=settings.OPENAI_API_KEY,
            temperature=0.6,
            response_format={"type": "json_object"},
        )

    async def start_session(
        self,
        interview_type: str,
        role: str,
        experience_level: str,
        topics: list[str],
        duration_minutes: int = 45,
    ) -> dict:
        session_id = str(uuid.uuid4())

        # Generate interview questions
        questions = await self._generate_questions(
            interview_type, role, experience_level, topics, duration_minutes
        )

        session_data = {
            "session_id": session_id,
            "user_id": str(self.user_id),
            "interview_type": interview_type,
            "role": role,
            "experience_level": experience_level,
            "topics": topics,
            "questions": questions,
            "current_index": 0,
            "answers": [],
            "started_at": __import__("datetime").datetime.utcnow().isoformat(),
        }
        await redis_manager.set(f"interview:{session_id}", session_data, ttl=duration_minutes * 60 + 300)

        first_question = questions[0] if questions else {}
        return {
            "session_id": session_id,
            "question": first_question.get("question", ""),
            "hints": first_question.get("hints", []),
            "expected_approach": first_question.get("approach", ""),
            "time_limit_minutes": first_question.get("time_minutes", 15),
        }

    async def evaluate_answer(self, session_id: uuid.UUID, answer: str) -> dict:
        session = await redis_manager.get(f"interview:{session_id}")
        if not session:
            return {"error": "Session not found or expired"}

        questions = session["questions"]
        idx = session["current_index"]
        current_q = questions[idx]

        # Evaluate the answer
        eval_prompt = f"""
Interview Question: {current_q['question']}
Expected Approach: {current_q.get('approach', '')}
Candidate Answer: {answer}

Evaluate the answer. Return JSON:
{{
  "score": 0-10,
  "feedback": "...",
  "strengths": [...],
  "improvements": [...],
  "follow_up_question": "..."
}}"""
        messages = [SystemMessage(content=INTERVIEWER_SYSTEM), HumanMessage(content=eval_prompt)]
        response = await self.llm.ainvoke(messages)
        evaluation = json.loads(response.content)

        session["answers"].append({"question": current_q["question"], "answer": answer, "evaluation": evaluation})
        session["current_index"] += 1

        # Check if interview is complete
        if session["current_index"] >= len(questions):
            final_score = sum(a["evaluation"].get("score", 0) for a in session["answers"]) / len(session["answers"])
            await redis_manager.delete(f"interview:{session_id}")
            return {
                "status": "completed",
                "final_score": final_score,
                "evaluation": evaluation,
                "summary": f"Interview completed. Overall score: {final_score:.1f}/10",
            }

        # Next question
        await redis_manager.set(f"interview:{session_id}", session, ttl=3600)
        next_q = questions[session["current_index"]]
        return {
            "status": "in_progress",
            "evaluation": evaluation,
            "next_question": next_q.get("question", ""),
            "hints": next_q.get("hints", []),
        }

    async def _generate_questions(
        self, interview_type: str, role: str, exp_level: str, topics: list, duration: int
    ) -> list[dict]:
        n_questions = max(2, duration // 15)
        prompt = f"""Generate {n_questions} {interview_type} interview questions for {role} ({exp_level} level).
Topics: {', '.join(topics)}
Return JSON array:
[{{"question": "...", "approach": "...", "hints": [...], "time_minutes": N, "difficulty": "easy|medium|hard"}}]"""

        messages = [SystemMessage(content=INTERVIEWER_SYSTEM), HumanMessage(content=prompt)]
        response = await self.llm.ainvoke(messages)
        data = json.loads(response.content)
        return data if isinstance(data, list) else data.get("questions", [])
