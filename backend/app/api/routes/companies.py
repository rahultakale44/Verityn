"""Company management API routes."""
from typing import Annotated
from fastapi import APIRouter, HTTPException, Query, status
from app.models.company import (
    CompanyCreate,
    CompanyUpdate,
    CompanyResponse,
    CompanyListResponse
)
from app.db.companies import (
    create_company,
    get_company,
    list_companies,
    update_company,
    delete_company,
    CompanyNotFoundError,
    DuplicateCompanyError,
    DatabaseConnectionError
)


router = APIRouter()


# Maximum page size to prevent excessive resource usage
MAX_PAGE_SIZE = 100
DEFAULT_PAGE_SIZE = 50


@router.post(
    "",
    response_model=CompanyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new company",
    responses={
        201: {"description": "Company created successfully"},
        409: {"description": "Company with same name or website already exists"},
        422: {"description": "Validation error"},
        503: {"description": "Database unavailable"}
    }
)
async def create_company_endpoint(company: CompanyCreate) -> CompanyResponse:
    """
    Create a new company record.
    
    Required fields:
    - company_name: Non-empty company name
    
    Optional fields:
    - website: Valid HTTP/HTTPS URL
    - industry: Industry sector
    - description: Company description
    - headquarters_country: Country location
    - headquarters_region: Region/state location
    - employee_count: Number of employees (non-negative)
    
    Duplicate detection:
    - Company name is normalized (case-insensitive, whitespace collapsed)
    - Website URL is normalized (case-insensitive, trailing slash removed)
    - Returns 409 if a company with the same normalized name or website exists
    """
    try:
        return create_company(company)
    except DuplicateCompanyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"message": str(e), "field": e.field}
        )
    except DatabaseConnectionError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not available"
        )


@router.get(
    "",
    response_model=CompanyListResponse,
    summary="List companies",
    responses={
        200: {"description": "List of companies"},
        503: {"description": "Database unavailable"}
    }
)
async def list_companies_endpoint(
    limit: Annotated[int, Query(ge=1, le=MAX_PAGE_SIZE)] = DEFAULT_PAGE_SIZE,
    offset: Annotated[int, Query(ge=0)] = 0
) -> CompanyListResponse:
    """
    List companies with pagination.
    
    Query parameters:
    - limit: Number of records to return (1-100, default 50)
    - offset: Number of records to skip (default 0)
    
    Returns:
    - items: List of company records
    - total: Total number of companies
    - limit: Requested page size
    - offset: Requested offset
    
    Companies are sorted by creation date, newest first.
    """
    try:
        companies, total = list_companies(limit=limit, offset=offset)
        return CompanyListResponse(
            items=companies,
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
    "/{company_id}",
    response_model=CompanyResponse,
    summary="Get a company by ID",
    responses={
        200: {"description": "Company found"},
        404: {"description": "Company not found"},
        422: {"description": "Invalid company ID format"},
        503: {"description": "Database unavailable"}
    }
)
async def get_company_endpoint(company_id: str) -> CompanyResponse:
    """
    Retrieve a single company by ID.
    
    Path parameters:
    - company_id: MongoDB ObjectId as string
    
    Returns the complete company record.
    """
    try:
        return get_company(company_id)
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
    except DatabaseConnectionError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not available"
        )


@router.patch(
    "/{company_id}",
    response_model=CompanyResponse,
    summary="Update a company",
    responses={
        200: {"description": "Company updated successfully"},
        404: {"description": "Company not found"},
        409: {"description": "Update would create duplicate"},
        422: {"description": "Invalid company ID or validation error"},
        503: {"description": "Database unavailable"}
    }
)
async def update_company_endpoint(
    company_id: str,
    update_data: CompanyUpdate
) -> CompanyResponse:
    """
    Update an existing company record.
    
    Path parameters:
    - company_id: MongoDB ObjectId as string
    
    All fields are optional. Only provided fields will be updated.
    The updated_at timestamp is automatically set to the current time.
    
    Cannot update:
    - id (immutable)
    - created_at (immutable)
    - updated_at (automatic)
    
    Duplicate detection applies to name and website changes.
    """
    try:
        return update_company(company_id, update_data)
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
    except DuplicateCompanyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"message": str(e), "field": e.field}
        )
    except DatabaseConnectionError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not available"
        )


@router.delete(
    "/{company_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a company",
    responses={
        204: {"description": "Company deleted successfully"},
        404: {"description": "Company not found"},
        422: {"description": "Invalid company ID format"},
        503: {"description": "Database unavailable"}
    }
)
async def delete_company_endpoint(company_id: str) -> None:
    """
    Delete a company record.
    
    Path parameters:
    - company_id: MongoDB ObjectId as string
    
    Returns 204 No Content on successful deletion.
    """
    try:
        delete_company(company_id)
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
    except DatabaseConnectionError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not available"
        )
