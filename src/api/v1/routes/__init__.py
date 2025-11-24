"""
Initialize API routes.
"""
from fastapi import APIRouter

# Create main API router
api_router = APIRouter()

# Import route modules AFTER creating api_router to avoid circular imports
from src.api.v1.routes.evaluation import router as evaluation_router
from src.api.v1.routes.ranking import router as ranking_router

# Include route modules
api_router.include_router(evaluation_router)
api_router.include_router(ranking_router)
