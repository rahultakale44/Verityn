"""Saved views API routes."""
from typing import Annotated
from fastapi import APIRouter, HTTPException, Query, Path, status
from app.models.saved_view import (
    SavedViewCreate,
    SavedViewUpdate,
    SavedViewResponse,
    SavedViewListResponse
)
from app.db.saved_views import (
    create_saved_view,
    get_saved_view,
    list_saved_views,
    update_saved_view,
    delete_saved_view,
    SavedViewNotFoundError
)
from app.db.companies import DatabaseConnectionError


router = APIRouter()


MAX_PAGE_SIZE = 100
DEFAULT_PAGE_SIZE = 50


@router.post(
    "",
    response_model=SavedViewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a saved view",
    responses={
        201: {"description": "Saved view created successfully"},
        422: {"description": "Invalid input data"},
        503: {"description": "Database unavailable"}
    }
)
async def create_saved_view_endpoint(
    data: SavedViewCreate
) -> SavedViewResponse:
    """
    Create a new saved view for lead intelligence filters.
    
    A saved view stores a named filter configuration that can be reloaded later.
    When a saved view is loaded, it applies the saved filters to the current data
    rather than storing stale copies of leads.
    
    **Request body:**
    - name: View name (required, max 200 chars)
    - description: Optional description (max 1000 chars)
    - filters: Filter configuration including:
      - icp_id: ICP ID to filter by (required)
      - outcomes: Qualification outcomes to include (optional)
      - min_score, max_score: Score range (optional)
      - min_evidence_coverage: Minimum evidence coverage (optional)
      - industries: Company industries (optional)
      - countries: Headquarters countries (optional)
      - min_employees, max_employees: Employee range (optional)
      - company_name_search: Name search term (optional)
      - has_research: Research availability filter (optional)
      - sort_by: Sort field (default: score)
      - sort_direction: Sort direction (default: desc)
    
    **Returns:**
    - Created saved view with ID and timestamps
    
    **Raises:**
    - 422: If validation fails
    - 503: If database connection not available
    """
    try:
        view = create_saved_view(
            name=data.name,
            filters=data.filters,
            description=data.description
        )
        return view
        
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
    "",
    response_model=SavedViewListResponse,
    summary="List saved views",
    responses={
        200: {"description": "List of saved views"},
        503: {"description": "Database unavailable"}
    }
)
async def list_saved_views_endpoint(
    limit: Annotated[int, Query(ge=1, le=MAX_PAGE_SIZE)] = DEFAULT_PAGE_SIZE,
    offset: Annotated[int, Query(ge=0)] = 0
) -> SavedViewListResponse:
    """
    List all saved views.
    
    Returns paginated list of saved views, newest first.
    
    **Query parameters:**
    - limit: Number of records to return (1-100, default 50)
    - offset: Number of records to skip (default 0)
    
    **Returns:**
    - items: List of saved views
    - total: Total number of saved views
    - Pagination metadata
    """
    try:
        views, total = list_saved_views(limit=limit, offset=offset)
        
        return SavedViewListResponse(
            items=views,
            total=total,
            limit=limit,
            offset=offset
        )
        
    except DatabaseConnectionError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not available"
        )


@router.get(
    "/{view_id}",
    response_model=SavedViewResponse,
    summary="Get saved view details",
    responses={
        200: {"description": "Saved view details"},
        404: {"description": "Saved view not found"},
        422: {"description": "Invalid ID format"},
        503: {"description": "Database unavailable"}
    }
)
async def get_saved_view_endpoint(
    view_id: Annotated[str, Path(description="Saved view ID")]
) -> SavedViewResponse:
    """
    Get details of a specific saved view.
    
    Returns the complete saved view including its filter configuration.
    
    **Path parameters:**
    - view_id: Saved view ID
    
    **Returns:**
    - Saved view with name, description, filters, and timestamps
    
    **Raises:**
    - 404: If saved view not found
    - 422: If ID format is invalid
    - 503: If database connection not available
    """
    try:
        view = get_saved_view(view_id)
        return view
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except SavedViewNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except DatabaseConnectionError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not available"
        )


@router.patch(
    "/{view_id}",
    response_model=SavedViewResponse,
    summary="Update saved view",
    responses={
        200: {"description": "Saved view updated successfully"},
        404: {"description": "Saved view not found"},
        422: {"description": "Invalid input data or ID format"},
        503: {"description": "Database unavailable"}
    }
)
async def update_saved_view_endpoint(
    view_id: Annotated[str, Path(description="Saved view ID")],
    data: SavedViewUpdate
) -> SavedViewResponse:
    """
    Update an existing saved view.
    
    Only provided fields are updated. To update filters, provide the complete
    new filter configuration.
    
    **Path parameters:**
    - view_id: Saved view ID
    
    **Request body (all optional):**
    - name: New view name
    - description: New description
    - filters: New filter configuration
    
    **Returns:**
    - Updated saved view
    
    **Raises:**
    - 404: If saved view not found
    - 422: If validation fails or ID format invalid
    - 503: If database connection not available
    """
    try:
        view = update_saved_view(
            view_id=view_id,
            name=data.name,
            description=data.description,
            filters=data.filters
        )
        return view
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except SavedViewNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except DatabaseConnectionError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not available"
        )


@router.delete(
    "/{view_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete saved view",
    responses={
        204: {"description": "Saved view deleted successfully"},
        404: {"description": "Saved view not found"},
        422: {"description": "Invalid ID format"},
        503: {"description": "Database unavailable"}
    }
)
async def delete_saved_view_endpoint(
    view_id: Annotated[str, Path(description="Saved view ID")]
) -> None:
    """
    Delete a saved view.
    
    This action cannot be undone.
    
    **Path parameters:**
    - view_id: Saved view ID
    
    **Returns:**
    - 204 No Content on success
    
    **Raises:**
    - 404: If saved view not found
    - 422: If ID format is invalid
    - 503: If database connection not available
    """
    try:
        delete_saved_view(view_id)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except SavedViewNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except DatabaseConnectionError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not available"
        )
