"""Research API routes."""
from typing import Annotated
from fastapi import APIRouter, HTTPException, Query, status, Path
from app.models.research import (
    ResearchRunResponse,
    ResearchRunListResponse,
    SourceEvidenceListResponse
)
from app.db.companies import (
    get_company,
    CompanyNotFoundError,
    DatabaseConnectionError
)
from app.db.research import (
    get_research_run,
    list_research_runs,
    list_source_evidence,
    ResearchNotFoundError
)
from app.services.research_service import research_service
from app.services.tavily_service import TavilyConfigurationError


router = APIRouter()


MAX_PAGE_SIZE = 100
DEFAULT_PAGE_SIZE = 50


@router.post(
    "/{company_id}/research",
    response_model=ResearchRunResponse,
    status_code=status.HTTP_200_OK,
    summary="Start research for a company",
    responses={
        200: {"description": "Research completed successfully"},
        404: {"description": "Company not found"},
        422: {"description": "Invalid company ID"},
        503: {"description": "Database or external service unavailable"}
    }
)
async def start_research(
    company_id: Annotated[str, Path(description="Company ID")]
) -> ResearchRunResponse:
    """
    Start a research run for an existing company.
    
    This endpoint performs a synchronous, bounded research operation:
    1. Validates the company exists
    2. Generates search queries based on company data
    3. Executes searches via Tavily API
    4. Saves source evidence to MongoDB
    5. Returns completed research run with status
    
    The client waits for the operation to complete. Research is bounded
    to a maximum of 5 search queries and runs with a timeout.
    
    Possible statuses:
    - completed: All searches succeeded
    - partial: Some searches succeeded, some failed
    - failed: No sources collected or configuration error
    
    Raises:
    - 404: If company does not exist
    - 422: If company ID is invalid
    - 503: If Tavily API is not configured or database unavailable
    """
    try:
        # Validate company exists
        company = get_company(company_id)
        
        # Conduct research (synchronous operation)
        research_run = research_service.conduct_research(company)
        
        return research_run
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except CompanyNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except TavilyConfigurationError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except DatabaseConnectionError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not available"
        )
    except Exception as e:
        # Log but don't expose internal details
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Research operation failed"
        )


@router.get(
    "/{company_id}/research",
    response_model=ResearchRunListResponse,
    summary="List research runs for a company",
    responses={
        200: {"description": "List of research runs"},
        422: {"description": "Invalid company ID"},
        503: {"description": "Database unavailable"}
    }
)
async def list_company_research(
    company_id: Annotated[str, Path(description="Company ID")],
    limit: Annotated[int, Query(ge=1, le=MAX_PAGE_SIZE)] = DEFAULT_PAGE_SIZE,
    offset: Annotated[int, Query(ge=0)] = 0
) -> ResearchRunListResponse:
    """
    List research run history for a company.
    
    Returns paginated list of research runs, newest first.
    
    Query parameters:
    - limit: Number of records to return (1-100, default 50)
    - offset: Number of records to skip (default 0)
    """
    try:
        runs, total = list_research_runs(
            company_id=company_id,
            limit=limit,
            offset=offset
        )
        
        return ResearchRunListResponse(
            items=runs,
            total=total,
            limit=limit,
            offset=offset
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except DatabaseConnectionError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not available"
        )


@router.get(
    "/{company_id}/research/{research_run_id}",
    response_model=ResearchRunResponse,
    summary="Get research run details",
    responses={
        200: {"description": "Research run details"},
        404: {"description": "Research run not found or doesn't belong to company"},
        422: {"description": "Invalid ID format"},
        503: {"description": "Database unavailable"}
    }
)
async def get_research_run_details(
    company_id: Annotated[str, Path(description="Company ID")],
    research_run_id: Annotated[str, Path(description="Research run ID")]
) -> ResearchRunResponse:
    """
    Get details of a specific research run.
    
    Validates that the research run belongs to the specified company.
    """
    try:
        research_run = get_research_run(
            research_run_id=research_run_id,
            company_id=company_id
        )
        
        return research_run
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except ResearchNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except DatabaseConnectionError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not available"
        )


@router.get(
    "/{company_id}/research/{research_run_id}/sources",
    response_model=SourceEvidenceListResponse,
    summary="List source evidence for a research run",
    responses={
        200: {"description": "List of source evidence"},
        422: {"description": "Invalid ID format"},
        503: {"description": "Database unavailable"}
    }
)
async def list_research_sources(
    company_id: Annotated[str, Path(description="Company ID")],
    research_run_id: Annotated[str, Path(description="Research run ID")],
    limit: Annotated[int, Query(ge=1, le=MAX_PAGE_SIZE)] = DEFAULT_PAGE_SIZE,
    offset: Annotated[int, Query(ge=0)] = 0
) -> SourceEvidenceListResponse:
    """
    List source evidence collected during a research run.
    
    Returns paginated list of sources, newest first.
    Validates that the research run belongs to the specified company.
    
    Query parameters:
    - limit: Number of records to return (1-100, default 50)
    - offset: Number of records to skip (default 0)
    """
    try:
        sources, total = list_source_evidence(
            research_run_id=research_run_id,
            company_id=company_id,
            limit=limit,
            offset=offset
        )
        
        return SourceEvidenceListResponse(
            items=sources,
            total=total,
            limit=limit,
            offset=offset
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except DatabaseConnectionError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not available"
        )
