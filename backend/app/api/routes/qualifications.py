"""Qualification API routes."""
from typing import Annotated
from fastapi import APIRouter, HTTPException, Query, status, Path
from app.models.qualification import (
    QualificationRequest,
    QualificationResponse,
    QualificationListResponse
)
from app.db.companies import (
    get_company,
    CompanyNotFoundError,
    DatabaseConnectionError
)
from app.db.icps import get_icp, ICPNotFoundError
from app.db.research import list_source_evidence
from app.db.qualifications import (
    create_qualification,
    get_qualification,
    list_qualifications,
    QualificationNotFoundError
)
from app.services.qualification_engine import qualify_company


router = APIRouter()


MAX_PAGE_SIZE = 100
DEFAULT_PAGE_SIZE = 50


@router.post(
    "/{company_id}/qualifications",
    response_model=QualificationResponse,
    status_code=status.HTTP_200_OK,
    summary="Qualify a company against an ICP",
    responses={
        200: {"description": "Qualification completed successfully"},
        404: {"description": "Company or ICP not found"},
        422: {"description": "Invalid ID format"},
        503: {"description": "Database unavailable"}
    }
)
async def qualify_company_endpoint(
    company_id: Annotated[str, Path(description="Company ID")],
    request: QualificationRequest
) -> QualificationResponse:
    """
    Qualify a company against an ICP configuration.
    
    This endpoint performs a deterministic qualification that:
    1. Retrieves the company record
    2. Retrieves the ICP configuration
    3. Retrieves available research evidence for the company
    4. Evaluates configured criteria using explicit matching rules
    5. Calculates score and evidence coverage
    6. Determines qualification outcome
    7. Stores the immutable qualification result
    8. Returns the complete qualification with criterion-level explanations
    
    Request body:
    - icp_id: ICP configuration to use for qualification
    
    Matching rules:
    - Industry: Case-insensitive exact match against accepted industries
    - Headquarters country: Case-insensitive exact match against accepted countries
    - Employee count: Inclusive range check (minimum <= count <= maximum)
    - Required keywords: At least one keyword must be found (case-insensitive, word-boundary aware)
    - Excluded keywords: If any excluded keyword found, it's a mismatch (disqualifying)
    
    Scoring:
    - Score = 100 × (earned_weight / evaluable_weight)
    - Only 'match' criteria contribute to earned_weight
    - 'match' and 'mismatch' criteria contribute to evaluable_weight
    - 'insufficient_evidence' and 'not_applicable' criteria are excluded from scoring
    
    Evidence coverage:
    - Evidence coverage = 100 × (evaluable_weight / total_enabled_weight)
    - Measures what percentage of enabled criteria had sufficient data
    
    Outcomes:
    - qualified: score >= qualification_threshold AND evidence_coverage >= minimum_evidence_coverage
    - partially_qualified: score >= partial_qualification_threshold but < qualification_threshold
    - not_qualified: score < partial_qualification_threshold OR excluded keyword found
    - insufficient_data: no criteria could be evaluated OR coverage too low for qualification
    
    Limitations:
    - Uses deterministic keyword and field matching only
    - Does not perform semantic analysis or claim verification
    - Research sources are search results, not independently verified facts
    - Missing data reported as insufficient evidence, not assumed
    
    Raises:
    - 404: If company or ICP does not exist
    - 422: If company_id or icp_id format is invalid
    - 503: If database connection not available
    """
    try:
        # Validate company exists
        company = get_company(company_id)
        
        # Validate ICP exists
        icp = get_icp(request.icp_id)
        
        # Retrieve research evidence for the company
        # We'll get sources from all research runs for this company
        # (In a real system, you might want to only use sources from recent/successful runs)
        sources = []
        try:
            # Get most recent sources (limit to reasonable number)
            sources_result, _ = list_source_evidence(
                research_run_id=None,  # We need to modify this to get all sources
                company_id=company_id,
                limit=100,
                offset=0
            )
            sources = sources_result
        except Exception:
            # If we can't get sources, continue with empty list
            # Qualification will mark criteria as insufficient_evidence
            pass
        
        # Actually, we need to get sources across all research runs
        # Let's modify the approach - get sources directly from collection
        from app.db.research import get_source_evidence_collection
        from bson import ObjectId
        
        try:
            sources_collection = get_source_evidence_collection()
            company_object_id = ObjectId(company_id)
            
            # Get all sources for this company, sorted by most recent
            source_docs = sources_collection.find(
                {"company_id": company_object_id}
            ).sort("retrieved_at", -1).limit(100)
            
            from app.db.research import source_evidence_to_response
            sources = [source_evidence_to_response(doc) for doc in source_docs]
        except Exception:
            # If we can't get sources, continue with empty list
            sources = []
        
        # Run qualification engine
        score, evidence_coverage, outcome, outcome_explanation, evaluations, limitations = qualify_company(
            company=company,
            sources=sources,
            icp=icp
        )
        
        # Create ICP snapshot (immutable copy)
        icp_snapshot = {
            "name": icp.name,
            "description": icp.description,
            "industries": icp.industries,
            "headquarters_countries": icp.headquarters_countries,
            "minimum_employee_count": icp.minimum_employee_count,
            "maximum_employee_count": icp.maximum_employee_count,
            "required_keywords": icp.required_keywords,
            "excluded_keywords": icp.excluded_keywords,
            "criteria_weights": icp.criteria_weights,
            "qualification_threshold": icp.qualification_threshold,
            "partial_qualification_threshold": icp.partial_qualification_threshold,
            "minimum_evidence_coverage": icp.minimum_evidence_coverage
        }
        
        # Store qualification result
        qualification = create_qualification(
            company_id=company_id,
            icp_id=request.icp_id,
            icp_snapshot=icp_snapshot,
            score=score,
            evidence_coverage=evidence_coverage,
            outcome=outcome,
            outcome_explanation=outcome_explanation,
            criteria_evaluations=evaluations,
            limitations=limitations
        )
        
        return qualification
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except (CompanyNotFoundError, ICPNotFoundError) as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
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
            detail="Qualification operation failed"
        )


@router.get(
    "/{company_id}/qualifications",
    response_model=QualificationListResponse,
    summary="List qualification results for a company",
    responses={
        200: {"description": "List of qualification results"},
        422: {"description": "Invalid company ID"},
        503: {"description": "Database unavailable"}
    }
)
async def list_qualifications_endpoint(
    company_id: Annotated[str, Path(description="Company ID")],
    limit: Annotated[int, Query(ge=1, le=MAX_PAGE_SIZE)] = DEFAULT_PAGE_SIZE,
    offset: Annotated[int, Query(ge=0)] = 0
) -> QualificationListResponse:
    """
    List qualification history for a company.
    
    Returns paginated list of qualification results, newest first.
    
    Each qualification includes:
    - Score and evidence coverage
    - Qualification outcome and explanation
    - Detailed criterion-level evaluations with evidence references
    - Immutable snapshot of ICP configuration used
    
    Query parameters:
    - limit: Number of records to return (1-100, default 50)
    - offset: Number of records to skip (default 0)
    """
    try:
        qualifications, total = list_qualifications(
            company_id=company_id,
            limit=limit,
            offset=offset
        )
        
        return QualificationListResponse(
            items=qualifications,
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
    "/{company_id}/qualifications/{qualification_id}",
    response_model=QualificationResponse,
    summary="Get qualification result details",
    responses={
        200: {"description": "Qualification result details"},
        404: {"description": "Qualification not found or doesn't belong to company"},
        422: {"description": "Invalid ID format"},
        503: {"description": "Database unavailable"}
    }
)
async def get_qualification_endpoint(
    company_id: Annotated[str, Path(description="Company ID")],
    qualification_id: Annotated[str, Path(description="Qualification ID")]
) -> QualificationResponse:
    """
    Get details of a specific qualification result.
    
    Validates that the qualification belongs to the specified company.
    
    The response includes:
    - Complete qualification result with score, coverage, and outcome
    - Criterion-level evaluations with statuses and explanations
    - Evidence references with source URLs, titles, and snippets
    - Immutable ICP snapshot showing configuration used
    - Known limitations of the qualification
    """
    try:
        qualification = get_qualification(
            qualification_id=qualification_id,
            company_id=company_id
        )
        
        return qualification
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except QualificationNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except DatabaseConnectionError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not available"
        )
