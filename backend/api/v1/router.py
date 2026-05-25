"""
API v1 router: aggregates all service routers.
"""
from fastapi import APIRouter

from api.v1.auth import router as auth_router
from api.v1.users import router as users_router
from api.v1.problems import router as problems_router
from api.v1.contests import router as contests_router
from api.v1.ai import router as ai_router
from api.v1.labs import router as labs_router
from api.v1.payments import router as payments_router
from api.v1.search import router as search_router
from api.v1.notifications import router as notifications_router
from api.v1.admin import router as admin_router

api_v1_router = APIRouter()

api_v1_router.include_router(auth_router)
api_v1_router.include_router(users_router)
api_v1_router.include_router(problems_router)
api_v1_router.include_router(contests_router)
api_v1_router.include_router(ai_router)
api_v1_router.include_router(labs_router)
api_v1_router.include_router(payments_router)
api_v1_router.include_router(search_router)
api_v1_router.include_router(notifications_router)
api_v1_router.include_router(admin_router)
