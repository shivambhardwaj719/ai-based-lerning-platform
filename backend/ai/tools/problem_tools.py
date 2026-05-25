"""LangChain custom tools for the AI agents — problem and knowledge retrieval."""
from __future__ import annotations

from typing import Any

from langchain_core.tools import tool


@tool
async def search_knowledge_base(query: str) -> str:
    """Search the knowledge base for explanations, concepts, and tutorials.

    Use this tool when the user asks about a concept, algorithm, or data structure.
    Returns the most relevant content from the vector database.
    """
    from ai.rag.retriever import KnowledgeRetriever
    retriever = KnowledgeRetriever()
    docs = await retriever.retrieve(query=query, limit=3)
    if not docs:
        return "No relevant content found in the knowledge base."
    return "\n\n---\n\n".join(
        f"**{d.get('title', 'Document')}**\n{d.get('content', '')}" for d in docs
    )


@tool
async def get_problem_hint(problem_id: str, hint_level: int = 1) -> str:
    """Get a hint for a specific problem without giving away the full solution.

    Args:
        problem_id: UUID of the problem.
        hint_level: 1 = conceptual hint, 2 = approach hint, 3 = pseudocode hint.
    """
    from core.database import database_manager
    from repositories.problem_repository import ProblemRepository
    import uuid

    try:
        pid = uuid.UUID(problem_id)
    except ValueError:
        return "Invalid problem ID."

    async with database_manager.session() as db:
        repo = ProblemRepository(db)
        problem = await repo.get_by_id(pid)
        if not problem:
            return "Problem not found."

    hint_prompts = {
        1: f"For the problem '{problem.title}': Think about which data structure or algorithm category this falls into. The difficulty is {problem.difficulty}.",
        2: f"For the problem '{problem.title}': Consider breaking the problem into sub-problems. Think about edge cases like empty inputs or single-element arrays.",
        3: f"For the problem '{problem.title}': Here is a high-level approach:\n1. Parse the input\n2. Apply a {problem.tags[0] if problem.tags else 'suitable'} technique\n3. Return the result in the required format.",
    }
    return hint_prompts.get(hint_level, hint_prompts[1])


@tool
async def get_user_progress(user_id: str) -> dict[str, Any]:
    """Retrieve the user's current skill level, solved problems, and weak areas.

    Use this to personalize responses based on what the user has already learned.
    """
    from core.database import database_manager
    from repositories.user_repository import UserRepository
    import uuid

    try:
        uid = uuid.UUID(user_id)
    except ValueError:
        return {"error": "Invalid user ID"}

    async with database_manager.session() as db:
        repo = UserRepository(db)
        user = await repo.get_with_profile(uid)
        if not user or not user.profile:
            return {"error": "User not found"}

    profile = user.profile
    return {
        "rating": profile.rating,
        "problems_solved": profile.problems_solved,
        "streak_days": profile.streak_days,
        "skills": user.skills or [],
        "total_points": profile.total_points,
    }


@tool
async def run_code_sample(code: str, language: str, test_input: str = "") -> str:
    """Execute a small code snippet and return the output.

    Use this when explaining code examples or verifying solutions.
    Only supports non-network, sandboxed execution.
    """
    from apps.code_execution.executor import CodeExecutor

    executor = CodeExecutor()
    result = await executor.execute(
        code=code,
        language=language,
        stdin=test_input,
    )
    if result.get("error"):
        return f"Execution error: {result['error']}"
    return f"Output:\n{result.get('stdout', '')}\nExecution time: {result.get('execution_time_ms', 0)}ms"
