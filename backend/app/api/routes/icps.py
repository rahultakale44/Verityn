"""ICP management API routes."""
from typing import Annotated
from fastapi import APIRouter, HTTPException, Query, status
from app.models.icp import (
    ICPCreate,
    ICPUpdate,
    ICPResponse,
    ICPListResponse
)
from app.db.icps import (
    create_icp,
    get_icp,
    list_icps,
    update_icp,
    delete_icp,
    ICPNotFoundError,
    DatabaseConnectionError
)


router = APIRouter()


MAX_PAGE_SIZE = 100
DEFAULT_PAGE_SIZE = 50


@router.post(
    "",
    response_model=ICPResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new ICP",
    responses={
        201: {"description": "ICP created successfully"},
        422: {"description": "Validation error"},
        503: {"description": "Database unavailable"}
    }
)
async def create_icp_endpoint(icp: ICPCreate) -> ICPResponse:
    """
    Create a new ICP (Ideal Customer Profile) configuration.
    
    Required fields:
    - name: Non-empty ICP name
    
    Optional fields:
    - description: ICP description
    - industries: List of accepted industries (case-insensitive matching)
    - headquarters_countries: List of accepted countries (case-insensitive matching)
    - minimum_employee_count: Minimum employee count (inclusive, non-negative)
    - maximum_employee_count: Maximum employee count (inclusive, non-negative, must be >= minimum)
    - required_keywords: List of keywords that must be present
    - excluded_keywords: List of keywords that disqualify if present
    - criteria_weights: Weight for each criterion (must be non-negative)
    - qualification_threshold: Minimum score for qualified (0-100, default 70)
    - partial_qualification_threshold: Minimum score for partial qualification (0-100, default 50)
    - minimum_evidence_coverage: Minimum evidence coverage required (0-100, default 60)
    
    Validation:
    - ICP name cannot be blank
    - Maximum employee count cannot be less than minimum
    - All weights must be non-negative
    - Partial threshold must not exceed qualification threshold
    """
    try:
        return create_icp(icp)
    except DatabaseConnectionError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not available"
        )


@router.get(
    "",
    response_model=ICPListResponse,
    summary="List ICPs",
    responses={
        200: {"description": "List of ICPs"},
        503: {"description": "Database unavailable"}
    }
)
async def list_icps_endpoint(
    limit: Annotated[int, Query(ge=1, le=MAX_PAGE_SIZE)] = DEFAULT_PAGE_SIZE,
    offset: Annotated[int, Query(ge=0)] = 0
) -> ICPListResponse:
    """
    List ICPs with pagination.
    
    Query parameters:
    - limit: Number of records to return (1-100, default 50)
    - offset: Number of records to skip (default 0)
    
    Returns:
    - items: List of ICP records
    - total: Total number of ICPs
    - limit: Requested page size
    - offset: Requested offset
    
    ICPs are sorted by creation date, newest first.
    """
    try:
        icps, total = list_icps(limit=limit, offset=offset)
        return ICPListResponse(
            items=icps,
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
    "/{icp_id}",
    response_model=ICPResponse,
    summary="Get an ICP by ID",
    responses={
        200: {"description": "ICP found"},
        404: {"description": "ICP not found"},
        422: {"description": "Invalid ICP ID format"},
        503: {"description": "Database unavailable"}
    }
)
async def get_icp_endpoint(icp_id: str) -> ICPResponse:
    """
    Retrieve a single ICP by ID.
    
    Path parameters:
    - icp_id: MongoDB ObjectId as string
    
    Returns the complete ICP configuration.
    """
    try:
        return get_icp(icp_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except ICPNotFoundError as e:
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
    "/{icp_id}",
    response_model=ICPResponse,
    summary="Update an ICP",
    responses={
        200: {"description": "ICP updated successfully"},
        404: {"description": "ICP not found"},
        422: {"description": "Invalid ICP ID or validation error"},
        503: {"description": "Database unavailable"}
    }
)
async def update_icp_endpoint(
    icp_id: str,
    update_data: ICPUpdate
) -> ICPResponse:
    """
    Update an existing ICP configuration.
    
    Path parameters:
    - icp_id: MongoDB ObjectId as string
    
    All fields are optional. Only provided fields will be updated.
    The updated_at timestamp is automatically set to the current time.
    
    Note: Updating an ICP does NOT affect historical qualification results.
    Historical results preserve an immutable snapshot of the ICP configuration
    used at the time of qualification.
    
    Cannot update:
    - id (immutable)
    - created_at (immutable)
    - updated_at (automatic)
    """
    try:
        return update_icp(icp_id, update_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except ICPNotFoundError as e:
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
    "/{icp_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an ICP",
    responses={
        204: {"description": "ICP deleted successfully"},
        404: {"description": "ICP not found"},
        422: {"description": "Invalid ICP ID format"},
        503: {"description": "Database unavailable"}
    }
)
async def delete_icp_endpoint(icp_id: str) -> None:
    """
    Delete an ICP configuration.
    
    Path parameters:
    - icp_id: MongoDB ObjectId as string
    
    Returns 204 No Content on successful deletion.
    
    Important: Deleting an ICP does NOT delete historical qualification results
    that reference it. Those results preserve an immutable snapshot of the ICP
    configuration, ensuring historical reproducibility.
    """
    try:
        delete_icp(icp_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except ICPNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except DatabaseConnectionError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not available"
        )
