"""
Lead ranking engine.

Provides deterministic ranking of companies based on qualification results.
Does not modify or recalculate qualification scores - only sorts existing results.
"""
from typing import Optional, Literal, Dict, List
from app.models.qualification import QualificationResponse


# Sort field options
SortField = Literal["score", "evidence_coverage", "qualified_at", "outcome"]

# Sort direction
SortDirection = Literal["asc", "desc"]

# Outcome ranking order (best to worst)
OUTCOME_RANK = {
    "qualified": 1,
    "partially_qualified": 2,
    "not_qualified": 3,
    "insufficient_data": 4
}


def get_sort_key_for_outcome(qual: QualificationResponse) -> int:
    """Get numeric sort key for qualification outcome."""
    return OUTCOME_RANK.get(qual.outcome, 999)


def rank_leads(
    qualifications: List[QualificationResponse],
    sort_by: SortField = "score",
    sort_direction: SortDirection = "desc"
) -> List[QualificationResponse]:
    """
    Rank leads deterministically based on qualification results.
    
    Sorting rules:
    - Primary sort: specified sort_by field in specified direction
    - Tie-breaker 1: qualified_at descending (newer first)
    - Tie-breaker 2: id ascending (stable, deterministic)
    
    Special handling:
    - score/evidence_coverage: None values sorted to end regardless of direction
    - outcome: sorted by quality order (qualified > partially_qualified > not_qualified > insufficient_data)
    
    Args:
        qualifications: List of qualification results to rank
        sort_by: Field to sort by (score, evidence_coverage, qualified_at, outcome)
        sort_direction: Sort direction (asc or desc)
        
    Returns:
        Sorted list of qualifications
        
    Examples:
        Sort by score descending (highest first):
        >>> rank_leads(quals, "score", "desc")
        
        Sort by evidence coverage ascending (lowest first):
        >>> rank_leads(quals, "evidence_coverage", "asc")
    """
    if not qualifications:
        return []
    
    # Build sort key function
    def sort_key(qual: QualificationResponse) -> tuple:
        """Generate sort key tuple for qualification."""
        
        # Primary sort field
        if sort_by == "score":
            # None scores go to end
            # Use tuple (has_value, value) so None always sorts to end
            if qual.score is None:
                if sort_direction == "desc":
                    primary = (1, 0)  # Has no value, sort to end
                else:
                    primary = (1, 0)  # Has no value, sort to end
            else:
                if sort_direction == "desc":
                    primary = (0, -qual.score)  # Negate for desc
                else:
                    primary = (0, qual.score)
        
        elif sort_by == "evidence_coverage":
            # None coverage goes to end
            if qual.evidence_coverage is None:
                if sort_direction == "desc":
                    primary = (1, 0)
                else:
                    primary = (1, 0)
            else:
                if sort_direction == "desc":
                    primary = (0, -qual.evidence_coverage)
                else:
                    primary = (0, qual.evidence_coverage)
        
        elif sort_by == "outcome":
            # Use outcome rank (qualified=1, partially_qualified=2, etc.)
            # Always sort by rank ascending (best first)
            outcome_rank = get_sort_key_for_outcome(qual)
            primary = (outcome_rank,)
        
        elif sort_by == "qualified_at":
            # Sort by timestamp
            if sort_direction == "desc":
                primary = (-qual.qualified_at.timestamp(),)
            else:
                primary = (qual.qualified_at.timestamp(),)
        
        else:
            # Default to qualified_at
            if sort_direction == "desc":
                primary = (-qual.qualified_at.timestamp(),)
            else:
                primary = (qual.qualified_at.timestamp(),)
        
        # Tie-breakers: qualified_at desc (newer first), then id asc
        tie_break_1 = -qual.qualified_at.timestamp()
        tie_break_2 = qual.id
        
        return (*primary, tie_break_1, tie_break_2)
    
    # Sort with constructed key (always ascending because we negate in key)
    sorted_quals = sorted(qualifications, key=sort_key)
    
    return sorted_quals


def get_latest_qualifications_per_company(
    qualifications: List[QualificationResponse]
) -> Dict[str, QualificationResponse]:
    """
    Get the latest qualification for each company.
    
    If multiple qualifications exist for the same company (with same or different ICPs),
    returns the most recent one based on qualified_at timestamp.
    
    Args:
        qualifications: List of all qualifications
        
    Returns:
        Dictionary mapping company_id to its latest qualification
        
    Notes:
        Uses qualified_at DESC as primary sort, then id ASC for stable tie-breaking.
    """
    latest_by_company: Dict[str, QualificationResponse] = {}
    
    for qual in qualifications:
        company_id = qual.company_id
        
        if company_id not in latest_by_company:
            latest_by_company[company_id] = qual
        else:
            # Compare timestamps
            existing = latest_by_company[company_id]
            if qual.qualified_at > existing.qualified_at:
                latest_by_company[company_id] = qual
            elif qual.qualified_at == existing.qualified_at:
                # Tie-break by id ascending
                if qual.id < existing.id:
                    latest_by_company[company_id] = qual
    
    return latest_by_company


def get_latest_qualification_for_icp(
    qualifications: List[QualificationResponse],
    icp_id: str
) -> Dict[str, QualificationResponse]:
    """
    Get the latest qualification for each company against a specific ICP.
    
    Filters qualifications to only those for the specified ICP,
    then returns the most recent qualification per company.
    
    Args:
        qualifications: List of all qualifications
        icp_id: ICP ID to filter by
        
    Returns:
        Dictionary mapping company_id to its latest qualification for the specified ICP
    """
    # Filter to specific ICP
    icp_quals = [q for q in qualifications if q.icp_id == icp_id]
    
    # Get latest per company
    return get_latest_qualifications_per_company(icp_quals)
