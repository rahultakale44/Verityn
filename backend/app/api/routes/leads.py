"""Lead intelligence API routes."""
from typing import Annotated, Optional, List
from fastapi import APIRouter, HTTPException, Query, status
from app.models.lead import LeadListResponse
from app.models.saved_view import SortField, SortDirection
from app.db.leads import get_ranked_leads
from app.db.companies import DatabaseConnectionError


router = APIRouter()


MAX_PAGE_SIZE = 100
DEFAULT_PAGE_SIZE = 50


@router.get(
    "",
    response_model=LeadListResponse,
    summary="Get ranked and filtered leads",
    responses={
        200: {"description": "Ranked list of leads"},
        422: {"description": "Invalid filter parameters"},
        503: {"description": "Database unavailable"}
    }
)
async def get_leads_endpoint(
    icp_id: Annotated[str, Query(description="ICP ID to filter by (required)")],
    sort_by: Annotated[SortField, Query(description="Field to sort by")] = "score",
    sort_direction: Annotated[SortDirection, Query(description="Sort direction")] = "desc",
    outcomes: Annotated[Optional[List[str]], Query(description="Qualification outcomes to include")] = None,
    min_score: Annotated[Optional[float], Query(ge=0.0, le=100.0, description="Minimum qualification score")] = None,
    max_score: Annotated[Optional[float], Query(ge=0.0, le=100.0, description="Maximum qualification score")] = None,
    min_evidence_coverage: Annotated[Optional[float], Query(ge=0.0, le=100.0, description="Minimum evidence coverage")] = None,
    industries: Annotated[Optional[List[str]], Query(description="Company industries to include")] = None,
    countries: Annotated[Optional[List[str]], Query(description="Company headquarters countries to include")] = None,
    min_employees: Annotated[Optional[int], Query(ge=0, description="Minimum employee count")] = None,
    max_employees: Annotated[Optional[int], Query(ge=0, description="Maximum employee count")] = None,
    company_name_search: Annotated[Optional[str], Query(max_length=200, description="Company name search term")] = None,
    has_research: Annotated[Optional[bool], Query(description="Filter by research availability")] = None,
    limit: Annotated[int, Query(ge=1, le=MAX_PAGE_SIZE)] = DEFAULT_PAGE_SIZE,
    offset: Annotated[int, Query(ge=0)] = 0
) -> LeadListResponse:
    """
    Get ranked and filtered leads for lead intelligence.
    
    This endpoint provides a unified view of companies with their latest qualification
    results against a specified ICP, along with comprehensive filtering and ranking.
    
    **Required Parameter:**
    - icp_id: The ICP to use for filtering and ranking
    
    **Ranking:**
    - Sorts leads by the specified sort_by field (score, evidence_coverage, qualified_at, outcome)
    - Uses stable tie-breaking: qualified_at DESC, then company_id ASC
    - Only includes companies that have been qualified against the specified ICP
    
    **Filtering:**
    - outcomes: Filter by qualification outcome (qualified, partially_qualified, not_qualified, insufficient_data)
    - min_score, max_score: Filter by qualification score range
    - min_evidence_coverage: Filter by minimum evidence coverage
    - industries: Filter by company industry (case-insensitive, exact match)
    - countries: Filter by headquarters country (case-insensitive, exact match)
    - min_employees, max_employees: Filter by employee count range
    - company_name_search: Search company name (case-insensitive, partial match)
    - has_research: Filter by research availability (true=has research, false=no research)
    
    **Pagination:**
    - limit: Number of results per page (1-100, default 50)
    - offset: Number of results to skip (default 0)
    
    **Response:**
    - items: List of leads with company and qualification data
    - total: Total number of leads matching filters
    - Pagination metadata
    
    **Important Notes:**
    - Only companies with a qualification for the specified ICP are included
    - The latest qualification per company is used
    - Scores are never recalculated - backend qualification engine is source of truth
    - None scores (insufficient_data) are handled appropriately in sorting
    - Research availability checks if any source_evidence records exist for the company
    
    **Raises:**
    - 422: If filter parameters are invalid
    - 503: If database connection not available
    """
    try:
        # Validate parameter combinations
        if min_score is not None and max_score is not None and min_score > max_score:
            raise ValueError("min_score cannot be greater than max_score")
        
        if min_employees is not None and max_employees is not None and min_employees > max_employees:
            raise ValueError("min_employees cannot be greater than max_employees")
        
        # Validate outcomes
        if outcomes:
            valid_outcomes = {"qualified", "partially_qualified", "not_qualified", "insufficient_data"}
            for outcome in outcomes:
                if outcome not in valid_outcomes:
                    raise ValueError(f"Invalid outcome: {outcome}")
        
        # Get ranked leads
        leads, total = get_ranked_leads(
            icp_id=icp_id,
            sort_by=sort_by,
            sort_direction=sort_direction,
            outcomes=outcomes,
            min_score=min_score,
            max_score=max_score,
            min_evidence_coverage=min_evidence_coverage,
            industries=industries,
            countries=countries,
            min_employees=min_employees,
            max_employees=max_employees,
            company_name_search=company_name_search,
            has_research=has_research,
            limit=limit,
            offset=offset
        )
        
        return LeadListResponse(
            items=leads,
            total=total,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_direction=sort_direction
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
    except Exception as e:
        # Log but don't expose internal details
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lead search operation failed"
        )
