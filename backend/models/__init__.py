"""Register all models for Alembic autogenerate and SQLAlchemy metadata."""
from models.user import User, Session, OAuthAccount, UserProfile, AuditLog
from models.problem import Problem, TestCase, Submission
from models.contest import Contest, ContestProblem, ContestParticipant, Leaderboard
from models.ai_conversation import AIConversation, AIMessage, Roadmap, StudyMaterial
from models.payment import Plan, Subscription, Payment
from models.lab import Lab, LabInstance, AIPlayground

__all__ = [
    "User", "Session", "OAuthAccount", "UserProfile", "AuditLog",
    "Problem", "TestCase", "Submission",
    "Contest", "ContestProblem", "ContestParticipant", "Leaderboard",
    "AIConversation", "AIMessage", "Roadmap", "StudyMaterial",
    "Plan", "Subscription", "Payment",
    "Lab", "LabInstance", "AIPlayground",
]
