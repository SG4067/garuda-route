"""Health-check endpoint."""

from fastapi import APIRouter

from app.config import settings

router = APIRouter()


@router.get("/health", tags=["health"], summary="Check API availability")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.environment,
    }
