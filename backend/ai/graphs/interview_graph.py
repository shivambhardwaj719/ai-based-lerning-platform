"""LangGraph StateGraph for the mock technical interview flow."""
from __future__ import annotations

from typing import Annotated, TypedDict

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages


class InterviewState(TypedDict):
    messages: Annotated[list, add_messages]
    phase: str                   # "intro" | "question" | "follow_up" | "debrief"
    question_count: int
    max_questions: int
    current_topic: str
    score: float
    feedback_notes: list[str]
    user_id: str


SYSTEM_PROMPT = """You are a senior software engineer conducting a realistic technical interview.
Your role is to:
1. Ask one focused coding or system design question at a time
2. Probe deeper with follow-up questions based on the candidate's answers
3. Evaluate correctness, complexity analysis, and communication clarity
4. Provide honest, constructive feedback at the end

Keep questions appropriate for the candidate's skill level.
Be encouraging but realistic — this is practice for real interviews."""


def _get_llm():
    return ChatAnthropic(model="claude-opus-4-7", temperature=0.7)


def intro_node(state: InterviewState) -> dict:
    """Introduce the interview and ask the first question."""
    llm = _get_llm()
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Start a technical interview for topic: {state['current_topic']}. Introduce yourself briefly and ask the first question."),
    ]
    response = llm.invoke(messages)
    return {
        "messages": [AIMessage(content=response.content)],
        "phase": "question",
        "question_count": 1,
    }


def question_node(state: InterviewState) -> dict:
    """Process candidate's answer and either follow-up or ask next question."""
    llm = _get_llm()
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]

    if state["question_count"] >= state["max_questions"]:
        messages.append(HumanMessage(content="Wrap up this question and transition to the debrief."))
        response = llm.invoke(messages)
        return {
            "messages": [AIMessage(content=response.content)],
            "phase": "debrief",
        }

    response = llm.invoke(messages)
    return {
        "messages": [AIMessage(content=response.content)],
        "phase": "follow_up" if state["question_count"] % 2 == 0 else "question",
        "question_count": state["question_count"] + 1,
    }


def debrief_node(state: InterviewState) -> dict:
    """Generate comprehensive interview feedback."""
    llm = _get_llm()
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        *state["messages"],
        HumanMessage(content="Provide a detailed debrief: overall score (1-10), strengths, areas for improvement, and specific recommendations."),
    ]
    response = llm.invoke(messages)

    # Extract score from response (heuristic)
    score = 7.0
    content = response.content
    for line in content.split("\n"):
        if "score" in line.lower() and any(c.isdigit() for c in line):
            try:
                score = float("".join(c for c in line if c.isdigit() or c == "."))
                score = min(10.0, max(1.0, score))
            except ValueError:
                pass

    return {
        "messages": [AIMessage(content=content)],
        "phase": "complete",
        "score": score,
    }


def route_phase(state: InterviewState) -> str:
    phase = state.get("phase", "intro")
    if phase == "intro":
        return "intro"
    if phase in ("question", "follow_up"):
        return "question"
    if phase == "debrief":
        return "debrief"
    return END


def build_interview_graph() -> StateGraph:
    graph = StateGraph(InterviewState)
    graph.add_node("intro", intro_node)
    graph.add_node("question", question_node)
    graph.add_node("debrief", debrief_node)

    graph.set_conditional_entry_point(route_phase, {
        "intro": "intro",
        "question": "question",
        "debrief": "debrief",
        END: END,
    })

    graph.add_conditional_edges("intro", route_phase, {
        "question": "question",
        "debrief": "debrief",
        END: END,
    })
    graph.add_conditional_edges("question", route_phase, {
        "question": "question",
        "debrief": "debrief",
        END: END,
    })
    graph.add_edge("debrief", END)

    checkpointer = MemorySaver()
    return graph.compile(checkpointer=checkpointer, interrupt_before=["question"])
