"""Verityn FastAPI application."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.mongodb import mongodb
from app.api.routes import health, companies, research, icps, qualifications, leads, saved_views
from app.db.companies import ensure_indexes
from app.db.research import ensure_research_indexes
from app.db.icps import ensure_icp_indexes
from app.db.qualifications import ensure_qualification_indexes
from app.db.saved_views import ensure_saved_views_indexes


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup: Initialize MongoDB connection
    mongodb.connect()
    # Create database indexes
    try:
        ensure_indexes()
        ensure_research_indexes()
        ensure_icp_indexes()
        ensure_qualification_indexes()
        ensure_saved_views_indexes()
    except Exception:
        # If index creation fails, log but continue
        # This allows the app to start even if MongoDB is unavailable
        pass
    yield
    # Shutdown: Close MongoDB connection
    mongodb.close()


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Evidence-Driven B2B Lead Intelligence Platform",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    health.router,
    prefix=f"/api/{settings.api_version}",
    tags=["health"]
)
app.include_router(
    companies.router,
    prefix=f"/api/{settings.api_version}/companies",
    tags=["companies"]
)
app.include_router(
    research.router,
    prefix=f"/api/{settings.api_version}/companies",
    tags=["research"]
)
app.include_router(
    icps.router,
    prefix=f"/api/{settings.api_version}/icps",
    tags=["icps"]
)
app.include_router(
    qualifications.router,
    prefix=f"/api/{settings.api_version}/companies",
    tags=["qualifications"]
)
app.include_router(
    leads.router,
    prefix=f"/api/{settings.api_version}/leads",
    tags=["leads"]
)
app.include_router(
    saved_views.router,
    prefix=f"/api/{settings.api_version}/saved-views",
    tags=["saved-views"]
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
