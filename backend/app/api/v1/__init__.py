"""API v1 routers."""
from fastapi import APIRouter
from .analyze import router as analyze_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(analyze_router)

__all__ = ["api_v1_router"]
