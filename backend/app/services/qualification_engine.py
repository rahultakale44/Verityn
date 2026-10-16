"""
Deterministic qualification engine.

This module implements pure, testable qualification logic that evaluates
companies against ICP configurations using explicit matching rules.

SCORING FORMULA:
- For each applicable criterion with status 'match', add its weight to earned_weight
- For each applicable criterion with status 'match' or 'mismatch', add its weight to evaluable_weight
- Criteria with status 'insufficient_evidence' or 'not_applicable' are excluded from both
- Score = 100 × (earned_weight / evaluable_weight) if evaluable_weight > 0, else None

EVIDENCE COVERAGE:
- Evidence coverage = 100 × (evaluable_weight / total_enabled_weight)
- Measures what percentage of enabled criteria had sufficient data to evaluate

OUTCOME CLASSIFICATION:
- insufficient_data: score is None (no criteria could be evaluated)
- not_qualified: score < partial_qualification_threshold OR excluded keyword found
- partially_qualified: partial_qualification_threshold <= score < qualification_threshold
- qualified: score >= qualification_threshold AND evidence_coverage >= minimum_evidence_coverage
"""
import re
from typing import Optional, Any
from app.models.company import CompanyResponse
from app.models.research import SourceEvidenceResponse
from app.models.icp import ICPResponse
from app.models.qualification import (
    CriterionEvaluation,
    EvidenceReference,
    CriterionStatus,
    QualificationOutcome
)


def normalize_for_matching(text: Optional[str]) -> str:
    """
    Normalize text for case-insensitive matching.
    
    Args:
        text: Text to normalize
        
    Returns:
        Lowercase, whitespace-collapsed string
    """
    if not text:
        return ""
    return " ".join(str(text).lower().split())


def check_keyword_in_text(keyword: str, text: str) -> bool:
    """
    Check if keyword appears in text (case-insensitive, word boundary aware).
    
    Args:
        keyword: Keyword to search for
        text: Text to search in
        
    Returns:
        True if keyword found
    """
    if not keyword or not text:
        return False
    
    # Escape special regex characters in keyword
    escaped_keyword = re.escape(keyword.lower())
    # Use word boundaries for more precise matching
    pattern = r'\b' + escaped_keyword + r'\b'
    
    return bool(re.search(pattern, text.lower()))


def evaluate_industry_criterion(
    company: CompanyResponse,
    icp: ICPResponse,
    weight: float
) -> CriterionEvaluation:
    """
    Evaluate industry match criterion.
    
    Args:
        company: Company record
        icp: ICP configuration
        weight: Criterion weight
        
    Returns:
        Criterion evaluation result
    """
    # Check if criterion is configured
    if not icp.industries or len(icp.industries) == 0:
        return CriterionEvaluation(
            criterion_id="industry",
            criterion_name="Industry Match",
            weight=weight,
            status="not_applicable",
            explanation="Industry matching not configured in ICP",
            observed_value=company.industry,
            expected_value=None
        )
    
    # Check if company has industry data
    if not company.industry:
        return CriterionEvaluation(
            criterion_id="industry",
            criterion_name="Industry Match",
            weight=weight,
            status="insufficient_evidence",
            explanation="Company industry not specified",
            observed_value=None,
            expected_value=icp.industries,
            reason_insufficient="Company profile does not include industry information"
        )
    
    # Normalize and compare
    company_industry_normalized = normalize_for_matching(company.industry)
    accepted_industries_normalized = [normalize_for_matching(ind) for ind in icp.industries]
    
    is_match = company_industry_normalized in accepted_industries_normalized
    
    return CriterionEvaluation(
        criterion_id="industry",
        criterion_name="Industry Match",
        weight=weight,
        status="match" if is_match else "mismatch",
        explanation=(
            f"Company industry '{company.industry}' matches accepted industries"
            if is_match else
            f"Company industry '{company.industry}' does not match accepted industries: {', '.join(icp.industries)}"
        ),
        observed_value=company.industry,
        expected_value=icp.industries
    )


def evaluate_headquarters_country_criterion(
    company: CompanyResponse,
    icp: ICPResponse,
    weight: float
) -> CriterionEvaluation:
    """
    Evaluate headquarters country match criterion.
    
    Args:
        company: Company record
        icp: ICP configuration
        weight: Criterion weight
        
    Returns:
        Criterion evaluation result
    """
    # Check if criterion is configured
    if not icp.headquarters_countries or len(icp.headquarters_countries) == 0:
        return CriterionEvaluation(
            criterion_id="headquarters_country",
            criterion_name="Headquarters Country Match",
            weight=weight,
            status="not_applicable",
            explanation="Headquarters country matching not configured in ICP",
            observed_value=company.headquarters_country,
            expected_value=None
        )
    
    # Check if company has country data
    if not company.headquarters_country:
        return CriterionEvaluation(
            criterion_id="headquarters_country",
            criterion_name="Headquarters Country Match",
            weight=weight,
            status="insufficient_evidence",
            explanation="Company headquarters country not specified",
            observed_value=None,
            expected_value=icp.headquarters_countries,
            reason_insufficient="Company profile does not include headquarters country"
        )
    
    # Normalize and compare
    company_country_normalized = normalize_for_matching(company.headquarters_country)
    accepted_countries_normalized = [normalize_for_matching(c) for c in icp.headquarters_countries]
    
    is_match = company_country_normalized in accepted_countries_normalized
    
    return CriterionEvaluation(
        criterion_id="headquarters_country",
        criterion_name="Headquarters Country Match",
        weight=weight,
        status="match" if is_match else "mismatch",
        explanation=(
            f"Company headquarters '{company.headquarters_country}' matches accepted countries"
            if is_match else
            f"Company headquarters '{company.headquarters_country}' does not match accepted countries: {', '.join(icp.headquarters_countries)}"
        ),
        observed_value=company.headquarters_country,
        expected_value=icp.headquarters_countries
    )


def evaluate_employee_count_criterion(
    company: CompanyResponse,
    icp: ICPResponse,
    weight: float
) -> CriterionEvaluation:
    """
    Evaluate employee count range criterion.
    
    Args:
        company: Company record
        icp: ICP configuration
        weight: Criterion weight
        
    Returns:
        Criterion evaluation result
    """
    # Check if criterion is configured
    if icp.minimum_employee_count is None and icp.maximum_employee_count is None:
        return CriterionEvaluation(
            criterion_id="employee_count",
            criterion_name="Employee Count Range",
            weight=weight,
            status="not_applicable",
            explanation="Employee count range not configured in ICP",
            observed_value=company.employee_count,
            expected_value=None
        )
    
    # Check if company has employee count
    if company.employee_count is None:
        return CriterionEvaluation(
            criterion_id="employee_count",
            criterion_name="Employee Count Range",
            weight=weight,
            status="insufficient_evidence",
            explanation="Company employee count not specified",
            observed_value=None,
            expected_value={
                "minimum": icp.minimum_employee_count,
                "maximum": icp.maximum_employee_count
            },
            reason_insufficient="Company profile does not include employee count"
        )
    
    # Check range
    min_count = icp.minimum_employee_count if icp.minimum_employee_count is not None else 0
    max_count = icp.maximum_employee_count if icp.maximum_employee_count is not None else float('inf')
    
    is_match = min_count <= company.employee_count <= max_count
    
    range_desc = f"{min_count}-{max_count if max_count != float('inf') else '∞'}"
    
    return CriterionEvaluation(
        criterion_id="employee_count",
        criterion_name="Employee Count Range",
        weight=weight,
        status="match" if is_match else "mismatch",
        explanation=(
            f"Company employee count ({company.employee_count}) is within range {range_desc}"
            if is_match else
            f"Company employee count ({company.employee_count}) is outside range {range_desc}"
        ),
        observed_value=company.employee_count,
        expected_value={
            "minimum": icp.minimum_employee_count,
            "maximum": icp.maximum_employee_count
        }
    )


def evaluate_required_keywords_criterion(
    company: CompanyResponse,
    sources: list[SourceEvidenceResponse],
    icp: ICPResponse,
    weight: float
) -> CriterionEvaluation:
    """
    Evaluate required keywords criterion.
    
    Searches company description and research source snippets for keywords.
    At least one required keyword must be found to match.
    
    Args:
        company: Company record
        sources: Research source evidence
        icp: ICP configuration
        weight: Criterion weight
        
    Returns:
        Criterion evaluation result
    """
    # Check if criterion is configured
    if not icp.required_keywords or len(icp.required_keywords) == 0:
        return CriterionEvaluation(
            criterion_id="required_keywords",
            criterion_name="Required Keywords",
            weight=weight,
            status="not_applicable",
            explanation="Required keywords not configured in ICP",
            observed_value=None,
            expected_value=None
        )
    
    # Build searchable text from company profile
    searchable_text_parts = []
    if company.description:
        searchable_text_parts.append(company.description)
    if company.industry:
        searchable_text_parts.append(company.industry)
    
    # Add source snippets
    evidence_refs = []
    for source in sources:
        searchable_text_parts.append(source.snippet)
    
    searchable_text = " ".join(searchable_text_parts)
    
    # Check if we have any text to search
    if not searchable_text.strip():
        return CriterionEvaluation(
            criterion_id="required_keywords",
            criterion_name="Required Keywords",
            weight=weight,
            status="insufficient_evidence",
            explanation="No company description or research sources available",
            observed_value=None,
            expected_value=icp.required_keywords,
            reason_insufficient="Company profile lacks description and no research sources collected"
        )
    
    # Check each keyword
    found_keywords = []
    for keyword in icp.required_keywords:
        if check_keyword_in_text(keyword, searchable_text):
            found_keywords.append(keyword)
            # Find which sources contained this keyword
            for source in sources:
                if check_keyword_in_text(keyword, source.snippet):
                    evidence_refs.append(EvidenceReference(
                        source_id=source.id,
                        source_url=source.source_url,
                        title=source.title,
                        snippet=source.snippet[:200] + "..." if len(source.snippet) > 200 else source.snippet
                    ))
                    break  # Only reference first source for each keyword
    
    # At least one keyword must be found
    is_match = len(found_keywords) > 0
    
    return CriterionEvaluation(
        criterion_id="required_keywords",
        criterion_name="Required Keywords",
        weight=weight,
        status="match" if is_match else "mismatch",
        explanation=(
            f"Found required keywords: {', '.join(found_keywords)}"
            if is_match else
            f"None of the required keywords found: {', '.join(icp.required_keywords)}"
        ),
        observed_value=found_keywords if found_keywords else None,
        expected_value=icp.required_keywords,
        evidence_references=evidence_refs
    )


def evaluate_excluded_keywords_criterion(
    company: CompanyResponse,
    sources: list[SourceEvidenceResponse],
    icp: ICPResponse,
    weight: float
) -> CriterionEvaluation:
    """
    Evaluate excluded keywords criterion.
    
    This is a disqualifying criterion - if any excluded keyword is found,
    it's a mismatch. If none are found, it's a match.
    
    Args:
        company: Company record
        sources: Research source evidence
        icp: ICP configuration
        weight: Criterion weight
        
    Returns:
        Criterion evaluation result
    """
    # Check if criterion is configured
    if not icp.excluded_keywords or len(icp.excluded_keywords) == 0:
        return CriterionEvaluation(
            criterion_id="excluded_keywords",
            criterion_name="Excluded Keywords",
            weight=weight,
            status="not_applicable",
            explanation="Excluded keywords not configured in ICP",
            observed_value=None,
            expected_value=None
        )
    
    # Build searchable text from company profile
    searchable_text_parts = []
    if company.description:
        searchable_text_parts.append(company.description)
    if company.industry:
        searchable_text_parts.append(company.industry)
    
    # Add source snippets
    evidence_refs = []
    for source in sources:
        searchable_text_parts.append(source.snippet)
    
    searchable_text = " ".join(searchable_text_parts)
    
    # Check if we have any text to search
    if not searchable_text.strip():
        # Insufficient data - can't verify excluded keywords
        return CriterionEvaluation(
            criterion_id="excluded_keywords",
            criterion_name="Excluded Keywords",
            weight=weight,
            status="insufficient_evidence",
            explanation="No company description or research sources to check for excluded keywords",
            observed_value=None,
            expected_value=icp.excluded_keywords,
            reason_insufficient="Cannot verify absence of excluded keywords without data"
        )
    
    # Check each excluded keyword
    found_excluded = []
    for keyword in icp.excluded_keywords:
        if check_keyword_in_text(keyword, searchable_text):
            found_excluded.append(keyword)
            # Find which sources contained this keyword
            for source in sources:
                if check_keyword_in_text(keyword, source.snippet):
                    evidence_refs.append(EvidenceReference(
                        source_id=source.id,
                        source_url=source.source_url,
                        title=source.title,
                        snippet=source.snippet[:200] + "..." if len(source.snippet) > 200 else source.snippet
                    ))
                    break
    
    # Match means no excluded keywords found
    is_match = len(found_excluded) == 0
    
    return CriterionEvaluation(
        criterion_id="excluded_keywords",
        criterion_name="Excluded Keywords",
        weight=weight,
        status="match" if is_match else "mismatch",
        explanation=(
            "No excluded keywords found"
            if is_match else
            f"Found excluded keywords: {', '.join(found_excluded)}"
        ),
        observed_value=found_excluded if found_excluded else None,
        expected_value=icp.excluded_keywords,
        evidence_references=evidence_refs
    )


def calculate_score_and_coverage(
    evaluations: list[CriterionEvaluation],
    icp: ICPResponse
) -> tuple[Optional[float], Optional[float]]:
    """
    Calculate qualification score and evidence coverage.
    
    Args:
        evaluations: List of criterion evaluations
        icp: ICP configuration
        
    Returns:
        Tuple of (score, evidence_coverage) or (None, None) if no evaluable criteria
    """
    earned_weight = 0.0
    evaluable_weight = 0.0
    total_enabled_weight = 0.0
    
    for evaluation in evaluations:
        # Total enabled weight includes all non-not_applicable criteria
        if evaluation.status != "not_applicable":
            total_enabled_weight += evaluation.weight
        
        # Evaluable weight includes match and mismatch (excludes insufficient_evidence)
        if evaluation.status in ["match", "mismatch"]:
            evaluable_weight += evaluation.weight
            
            # Earned weight only for matches
            if evaluation.status == "match":
                earned_weight += evaluation.weight
    
    # Calculate score
    if evaluable_weight > 0:
        score = 100.0 * (earned_weight / evaluable_weight)
    else:
        score = None
    
    # Calculate evidence coverage
    if total_enabled_weight > 0:
        evidence_coverage = 100.0 * (evaluable_weight / total_enabled_weight)
    else:
        evidence_coverage = None
    
    return score, evidence_coverage


def determine_outcome(
    score: Optional[float],
    evidence_coverage: Optional[float],
    evaluations: list[CriterionEvaluation],
    icp: ICPResponse
) -> tuple[QualificationOutcome, str]:
    """
    Determine qualification outcome based on score, coverage, and evaluations.
    
    Args:
        score: Calculated score (0-100 or None)
        evidence_coverage: Evidence coverage percentage (0-100 or None)
        evaluations: List of criterion evaluations
        icp: ICP configuration
        
    Returns:
        Tuple of (outcome, explanation)
    """
    # Check for insufficient data
    if score is None:
        return (
            "insufficient_data",
            "No criteria could be evaluated due to lack of company data or research evidence"
        )
    
    # Check for hard disqualification (excluded keyword found)
    excluded_eval = next(
        (e for e in evaluations if e.criterion_id == "excluded_keywords" and e.status == "mismatch"),
        None
    )
    if excluded_eval:
        return (
            "not_qualified",
            f"Disqualified: {excluded_eval.explanation}"
        )
    
    # Check qualification threshold
    if score >= icp.qualification_threshold:
        # Need sufficient evidence coverage for qualification
        if evidence_coverage is not None and evidence_coverage >= icp.minimum_evidence_coverage:
            return (
                "qualified",
                f"Score {score:.1f} meets threshold {icp.qualification_threshold} "
                f"with {evidence_coverage:.1f}% evidence coverage"
            )
        else:
            return (
                "insufficient_data",
                f"Score {score:.1f} meets threshold but evidence coverage "
                f"({evidence_coverage:.1f}%) is below minimum ({icp.minimum_evidence_coverage}%)"
            )
    
    # Check partial qualification threshold
    if score >= icp.partial_qualification_threshold:
        return (
            "partially_qualified",
            f"Score {score:.1f} meets partial threshold {icp.partial_qualification_threshold} "
            f"but not full threshold {icp.qualification_threshold}"
        )
    
    # Not qualified
    return (
        "not_qualified",
        f"Score {score:.1f} below partial qualification threshold {icp.partial_qualification_threshold}"
    )


def qualify_company(
    company: CompanyResponse,
    sources: list[SourceEvidenceResponse],
    icp: ICPResponse
) -> tuple[Optional[float], Optional[float], QualificationOutcome, str, list[CriterionEvaluation], Optional[str]]:
    """
    Qualify a company against an ICP.
    
    This is a pure function that performs deterministic qualification.
    
    Args:
        company: Company to qualify
        sources: Research source evidence for the company
        icp: ICP configuration
        
    Returns:
        Tuple of (score, evidence_coverage, outcome, outcome_explanation, criteria_evaluations, limitations)
    """
    # Evaluate each criterion
    evaluations = []
    
    # Industry
    if "industry" in icp.criteria_weights:
        evaluations.append(evaluate_industry_criterion(
            company, icp, icp.criteria_weights["industry"]
        ))
    
    # Headquarters country
    if "headquarters_country" in icp.criteria_weights:
        evaluations.append(evaluate_headquarters_country_criterion(
            company, icp, icp.criteria_weights["headquarters_country"]
        ))
    
    # Employee count
    if "employee_count" in icp.criteria_weights:
        evaluations.append(evaluate_employee_count_criterion(
            company, icp, icp.criteria_weights["employee_count"]
        ))
    
    # Required keywords
    if "required_keywords" in icp.criteria_weights:
        evaluations.append(evaluate_required_keywords_criterion(
            company, sources, icp, icp.criteria_weights["required_keywords"]
        ))
    
    # Excluded keywords
    if "excluded_keywords" in icp.criteria_weights:
        evaluations.append(evaluate_excluded_keywords_criterion(
            company, sources, icp, icp.criteria_weights["excluded_keywords"]
        ))
    
    # Calculate score and coverage
    score, evidence_coverage = calculate_score_and_coverage(evaluations, icp)
    
    # Determine outcome
    outcome, outcome_explanation = determine_outcome(score, evidence_coverage, evaluations, icp)
    
    # Build limitations message
    limitations_parts = []
    
    # Check for insufficient evidence
    insufficient_count = sum(1 for e in evaluations if e.status == "insufficient_evidence")
    if insufficient_count > 0:
        limitations_parts.append(
            f"{insufficient_count} criterion/criteria had insufficient evidence to evaluate"
        )
    
    # Note deterministic matching
    limitations_parts.append(
        "Qualification uses deterministic keyword and field matching; "
        "it does not perform semantic analysis or claim verification"
    )
    
    # Note source material nature
    if any(e.evidence_references for e in evaluations):
        limitations_parts.append(
            "Research sources are search results and web content, not independently verified facts"
        )
    
    limitations = ". ".join(limitations_parts) if limitations_parts else None
    
    return score, evidence_coverage, outcome, outcome_explanation, evaluations, limitations
