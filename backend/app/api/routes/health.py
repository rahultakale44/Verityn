"""Health check endpoint."""
from fastapi import APIRouter
from pydantic import BaseModel
from app.core.config import settings


router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model."""
    app_name: str
    status: str
    version: str


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.
    
    Returns application name, status, and version.
    Does not check external dependencies.
    """
    return HealthResponse(
        app_name=settings.app_name,
        status="healthy",
        version=settings.app_version
    )
