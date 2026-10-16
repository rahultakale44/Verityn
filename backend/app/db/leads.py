"""Lead intelligence data access layer."""
from typing import Optional, List
from bson import ObjectId
from app.db.mongodb import mongodb
from app.db.companies import DatabaseConnectionError
from app.models.lead import LeadResponse
from app.models.saved_view import SortField, SortDirection


def get_leads_collection():
    """Get database handle for aggregation queries."""
    db = mongodb.get_database()
    if db is None:
        raise DatabaseConnectionError("Database connection not available")
    return db


def build_match_stage(
    icp_id: str,
    outcomes: Optional[List[str]] = None,
    min_score: Optional[float] = None,
    max_score: Optional[float] = None,
    min_evidence_coverage: Optional[float] = None,
    industries: Optional[List[str]] = None,
    countries: Optional[List[str]] = None,
    min_employees: Optional[int] = None,
    max_employees: Optional[int] = None,
    company_name_search: Optional[str] = None,
    has_research: Optional[bool] = None
) -> dict:
    """
    Build MongoDB match stage for filtering leads.
    
    Args:
        icp_id: ICP ID to filter by (required)
        outcomes: Qualification outcomes to include
        min_score: Minimum qualification score
        max_score: Maximum qualification score
        min_evidence_coverage: Minimum evidence coverage
        industries: Company industries to include
        countries: Company headquarters countries to include
        min_employees: Minimum employee count
        max_employees: Maximum employee count
        company_name_search: Company name search term (case-insensitive)
        has_research: Filter by research availability
        
    Returns:
        MongoDB match stage dictionary
    """
    match_conditions = {}
    
    # ICP filter (required)
    try:
        match_conditions["qualification.icp_id"] = ObjectId(icp_id)
    except Exception:
        raise ValueError(f"Invalid ICP ID format: {icp_id}")
    
    # Outcome filter
    if outcomes:
        match_conditions["qualification.outcome"] = {"$in": outcomes}
    
    # Score filters
    if min_score is not None or max_score is not None:
        score_conditions = {}
        if min_score is not None:
            score_conditions["$gte"] = min_score
        if max_score is not None:
            score_conditions["$lte"] = max_score
        if score_conditions:
            match_conditions["qualification.score"] = score_conditions
    
    # Evidence coverage filter
    if min_evidence_coverage is not None:
        match_conditions["qualification.evidence_coverage"] = {"$gte": min_evidence_coverage}
    
    # Industry filter (case-insensitive)
    if industries:
        # Create case-insensitive regex pattern for each industry
        industry_patterns = [{"$regex": f"^{industry}$", "$options": "i"} for industry in industries]
        match_conditions["company.industry"] = {"$in": industry_patterns}
    
    # Country filter (case-insensitive)
    if countries:
        country_patterns = [{"$regex": f"^{country}$", "$options": "i"} for country in countries]
        match_conditions["company.headquarters_country"] = {"$in": country_patterns}
    
    # Employee count range
    if min_employees is not None or max_employees is not None:
        employee_conditions = {}
        if min_employees is not None:
            employee_conditions["$gte"] = min_employees
        if max_employees is not None:
            employee_conditions["$lte"] = max_employees
        if employee_conditions:
            match_conditions["company.employee_count"] = employee_conditions
    
    # Company name search (case-insensitive partial match)
    if company_name_search:
        match_conditions["company.company_name"] = {
            "$regex": company_name_search,
            "$options": "i"
        }
    
    # Research availability filter
    if has_research is not None:
        if has_research:
            match_conditions["research_count"] = {"$gt": 0}
        else:
            match_conditions["research_count"] = 0
    
    return match_conditions


def build_sort_stage(sort_by: SortField, sort_direction: SortDirection) -> List[tuple]:
    """
    Build MongoDB sort specification.
    
    Returns sort stages with tie-breakers:
    - Primary: specified sort field
    - Tie-breaker 1: qualified_at descending (newer first)
    - Tie-breaker 2: company_id ascending (stable)
    
    Args:
        sort_by: Field to sort by
        sort_direction: Sort direction
        
    Returns:
        List of (field, direction) tuples for MongoDB sort
    """
    direction = 1 if sort_direction == "asc" else -1
    
    # Map sort field to database path
    field_map = {
        "score": "qualification.score",
        "evidence_coverage": "qualification.evidence_coverage",
        "qualified_at": "qualification.qualified_at",
        "outcome": "qualification.outcome"
    }
    
    primary_field = field_map.get(sort_by, "qualification.score")
    
    # Build sort specification with tie-breakers
    sort_spec = [
        (primary_field, direction),
        ("qualification.qualified_at", -1),  # Always desc for tie-break
        ("company._id", 1)  # Always asc for stable sort
    ]
    
    return sort_spec


def get_ranked_leads(
    icp_id: str,
    sort_by: SortField = "score",
    sort_direction: SortDirection = "desc",
    outcomes: Optional[List[str]] = None,
    min_score: Optional[float] = None,
    max_score: Optional[float] = None,
    min_evidence_coverage: Optional[float] = None,
    industries: Optional[List[str]] = None,
    countries: Optional[List[str]] = None,
    min_employees: Optional[int] = None,
    max_employees: Optional[int] = None,
    company_name_search: Optional[str] = None,
    has_research: Optional[bool] = None,
    limit: int = 50,
    offset: int = 0
) -> tuple[list[LeadResponse], int]:
    """
    Get ranked and filtered leads using MongoDB aggregation.
    
    This function:
    1. Finds the latest qualification per company for the specified ICP
    2. Joins with company data
    3. Checks research availability
    4. Applies filters
    5. Sorts with stable tie-breaking
    6. Returns paginated results
    
    Args:
        icp_id: ICP ID to filter by (required)
        sort_by: Field to sort by (score, evidence_coverage, qualified_at, outcome)
        sort_direction: Sort direction (asc or desc)
        outcomes: Qualification outcomes to include
        min_score: Minimum qualification score
        max_score: Maximum qualification score
        min_evidence_coverage: Minimum evidence coverage
        industries: Company industries to include
        countries: Company headquarters countries to include
        min_employees: Minimum employee count
        max_employees: Maximum employee count
        company_name_search: Company name search term
        has_research: Filter by research availability
        limit: Maximum number of results to return
        offset: Number of results to skip
        
    Returns:
        Tuple of (list of leads, total count)
        
    Raises:
        ValueError: If icp_id or other parameters are invalid
        DatabaseConnectionError: If database is not available
    """
    db = get_leads_collection()
    
    # Convert ICP ID
    try:
        icp_object_id = ObjectId(icp_id)
    except Exception:
        raise ValueError(f"Invalid ICP ID format: {icp_id}")
    
    # Build aggregation pipeline
    pipeline = []
    
    # Stage 1: Filter qualifications by ICP and get latest per company
    pipeline.append({
        "$match": {
            "icp_id": icp_object_id
        }
    })
    
    # Stage 2: Sort by qualified_at desc to get latest
    pipeline.append({
        "$sort": {"company_id": 1, "qualified_at": -1}
    })
    
    # Stage 3: Group by company_id to get latest qualification
    pipeline.append({
        "$group": {
            "_id": "$company_id",
            "qualification": {"$first": "$$ROOT"}
        }
    })
    
    # Stage 4: Lookup company data
    pipeline.append({
        "$lookup": {
            "from": "companies",
            "localField": "_id",
            "foreignField": "_id",
            "as": "company"
        }
    })
    
    # Stage 5: Unwind company (should always be 1)
    pipeline.append({
        "$unwind": "$company"
    })
    
    # Stage 6: Lookup ICP data for name
    pipeline.append({
        "$lookup": {
            "from": "icps",
            "localField": "qualification.icp_id",
            "foreignField": "_id",
            "as": "icp"
        }
    })
    
    # Stage 7: Unwind ICP
    pipeline.append({
        "$unwind": "$icp"
    })
    
    # Stage 8: Lookup research availability
    pipeline.append({
        "$lookup": {
            "from": "source_evidence",
            "localField": "_id",
            "foreignField": "company_id",
            "as": "research_sources"
        }
    })
    
    # Stage 9: Add research count
    pipeline.append({
        "$addFields": {
            "research_count": {"$size": "$research_sources"}
        }
    })
    
    # Stage 10: Build match conditions for filters
    match_conditions = build_match_stage(
        icp_id=icp_id,
        outcomes=outcomes,
        min_score=min_score,
        max_score=max_score,
        min_evidence_coverage=min_evidence_coverage,
        industries=industries,
        countries=countries,
        min_employees=min_employees,
        max_employees=max_employees,
        company_name_search=company_name_search,
        has_research=has_research
    )
    
    # Remove icp_id from match since we already filtered
    if "qualification.icp_id" in match_conditions:
        del match_conditions["qualification.icp_id"]
    
    if match_conditions:
        pipeline.append({"$match": match_conditions})
    
    # Stage 11: Count total matching documents (before pagination)
    count_pipeline = pipeline + [{"$count": "total"}]
    count_result = list(db.qualifications.aggregate(count_pipeline))
    total = count_result[0]["total"] if count_result else 0
    
    # Stage 12: Sort results
    sort_spec = build_sort_stage(sort_by, sort_direction)
    pipeline.append({"$sort": dict(sort_spec)})
    
    # Stage 13: Pagination
    pipeline.append({"$skip": offset})
    pipeline.append({"$limit": limit})
    
    # Stage 14: Project to LeadResponse format
    pipeline.append({
        "$project": {
            "company_id": {"$toString": "$company._id"},
            "company_name": "$company.company_name",
            "website": "$company.website",
            "industry": "$company.industry",
            "headquarters_country": "$company.headquarters_country",
            "headquarters_region": "$company.headquarters_region",
            "employee_count": "$company.employee_count",
            "qualification_id": {"$toString": "$qualification._id"},
            "icp_id": {"$toString": "$qualification.icp_id"},
            "icp_name": "$icp.name",
            "qualified_at": "$qualification.qualified_at",
            "score": "$qualification.score",
            "evidence_coverage": "$qualification.evidence_coverage",
            "outcome": "$qualification.outcome",
            "outcome_explanation": "$qualification.outcome_explanation",
            "has_research": {"$gt": ["$research_count", 0]}
        }
    })
    
    # Execute aggregation
    results = list(db.qualifications.aggregate(pipeline))
    
    # Convert to LeadResponse objects
    leads = [LeadResponse(**doc) for doc in results]
    
    return leads, total
