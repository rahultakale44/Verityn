"""Tests for the qualification engine."""
import pytest
from datetime import datetime, timezone
from app.models.company import CompanyResponse
from app.models.research import SourceEvidenceResponse
from app.models.icp import ICPResponse
from app.services.qualification_engine import (
    normalize_for_matching,
    check_keyword_in_text,
    evaluate_industry_criterion,
    evaluate_headquarters_country_criterion,
    evaluate_employee_count_criterion,
    evaluate_required_keywords_criterion,
    evaluate_excluded_keywords_criterion,
    calculate_score_and_coverage,
    determine_outcome,
    qualify_company
)


@pytest.fixture
def sample_company():
    """Sample company for testing."""
    return CompanyResponse(
        id="507f1f77bcf86cd799439011",
        company_name="Acme Corporation",
        website="https://acme.com",
        industry="Software",
        description="Enterprise SaaS platform for B2B companies",
        headquarters_country="United States",
        headquarters_region="California",
        employee_count=500,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )


@pytest.fixture
def sample_icp():
    """Sample ICP for testing."""
    return ICPResponse(
        id="507f1f77bcf86cd799439012",
        name="Enterprise SaaS",
        description="Target enterprise SaaS companies",
        industries=["Software", "Technology"],
        headquarters_countries=["United States", "Canada"],
        minimum_employee_count=100,
        maximum_employee_count=1000,
        required_keywords=["enterprise", "B2B"],
        excluded_keywords=["consumer", "B2C"],
        criteria_weights={
            "industry": 20.0,
            "headquarters_country": 15.0,
            "employee_count": 25.0,
            "required_keywords": 30.0,
            "excluded_keywords": 10.0
        },
        qualification_threshold=70.0,
        partial_qualification_threshold=50.0,
        minimum_evidence_coverage=60.0,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )


@pytest.fixture
def sample_sources():
    """Sample research sources for testing."""
    now = datetime.now(timezone.utc)
    return [
        SourceEvidenceResponse(
            id="507f1f77bcf86cd799439013",
            research_run_id="507f1f77bcf86cd799439014",
            company_id="507f1f77bcf86cd799439011",
            source_url="https://example.com/article1",
            source_domain="example.com",
            title="Acme Corp expands enterprise offerings",
            snippet="Acme Corporation announced expansion of their enterprise B2B platform",
            published_at=None,
            retrieved_at=now,
            provider="Tavily",
            content_type=None
        )
    ]


def test_normalize_for_matching():
    """Test text normalization for matching."""
    assert normalize_for_matching("Software") == "software"
    assert normalize_for_matching("  Multiple   Spaces  ") == "multiple spaces"
    assert normalize_for_matching(None) == ""
    assert normalize_for_matching("") == ""


def test_check_keyword_in_text():
    """Test keyword matching with word boundaries."""
    text = "Enterprise software for B2B companies"
    
    assert check_keyword_in_text("enterprise", text) is True
    assert check_keyword_in_text("software", text) is True
    assert check_keyword_in_text("B2B", text) is True
    assert check_keyword_in_text("consumer", text) is False
    
    # Word boundary test
    assert check_keyword_in_text("soft", text) is False  # Not full word


def test_evaluate_industry_match(sample_company, sample_icp):
    """Test industry criterion evaluation - match."""
    result = evaluate_industry_criterion(sample_company, sample_icp, 20.0)
    
    assert result.criterion_id == "industry"
    assert result.status == "match"
    assert result.weight == 20.0
    assert result.observed_value == "Software"


def test_evaluate_industry_mismatch(sample_company, sample_icp):
    """Test industry criterion evaluation - mismatch."""
    company = CompanyResponse(
        **{**sample_company.model_dump(), "industry": "Healthcare"}
    )
    
    result = evaluate_industry_criterion(company, sample_icp, 20.0)
    
    assert result.status == "mismatch"
    assert result.observed_value == "Healthcare"


def test_evaluate_industry_insufficient_evidence(sample_company, sample_icp):
    """Test industry criterion - insufficient evidence."""
    company = CompanyResponse(
        **{**sample_company.model_dump(), "industry": None}
    )
    
    result = evaluate_industry_criterion(company, sample_icp, 20.0)
    
    assert result.status == "insufficient_evidence"
    assert result.observed_value is None
    assert result.reason_insufficient is not None


def test_evaluate_industry_not_applicable(sample_company):
    """Test industry criterion - not applicable."""
    icp = ICPResponse(
        id="507f1f77bcf86cd799439012",
        name="Test ICP",
        description=None,
        industries=None,  # Not configured
        headquarters_countries=None,
        minimum_employee_count=None,
        maximum_employee_count=None,
        required_keywords=None,
        excluded_keywords=None,
        criteria_weights={"industry": 20.0},
        qualification_threshold=70.0,
        partial_qualification_threshold=50.0,
        minimum_evidence_coverage=60.0,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    
    result = evaluate_industry_criterion(sample_company, icp, 20.0)
    
    assert result.status == "not_applicable"


def test_evaluate_headquarters_country_match(sample_company, sample_icp):
    """Test headquarters country criterion - match."""
    result = evaluate_headquarters_country_criterion(sample_company, sample_icp, 15.0)
    
    assert result.status == "match"
    assert result.observed_value == "United States"


def test_evaluate_headquarters_country_mismatch(sample_company, sample_icp):
    """Test headquarters country criterion - mismatch."""
    company = CompanyResponse(
        **{**sample_company.model_dump(), "headquarters_country": "Germany"}
    )
    
    result = evaluate_headquarters_country_criterion(company, sample_icp, 15.0)
    
    assert result.status == "mismatch"


def test_evaluate_employee_count_match(sample_company, sample_icp):
    """Test employee count criterion - match."""
    result = evaluate_employee_count_criterion(sample_company, sample_icp, 25.0)
    
    assert result.status == "match"
    assert result.observed_value == 500


def test_evaluate_employee_count_below_minimum(sample_company, sample_icp):
    """Test employee count criterion - below minimum."""
    company = CompanyResponse(
        **{**sample_company.model_dump(), "employee_count": 50}
    )
    
    result = evaluate_employee_count_criterion(company, sample_icp, 25.0)
    
    assert result.status == "mismatch"


def test_evaluate_employee_count_above_maximum(sample_company, sample_icp):
    """Test employee count criterion - above maximum."""
    company = CompanyResponse(
        **{**sample_company.model_dump(), "employee_count": 2000}
    )
    
    result = evaluate_employee_count_criterion(company, sample_icp, 25.0)
    
    assert result.status == "mismatch"


def test_evaluate_employee_count_at_boundaries(sample_company, sample_icp):
    """Test employee count criterion - at range boundaries."""
    # At minimum
    company_min = CompanyResponse(
        **{**sample_company.model_dump(), "employee_count": 100}
    )
    result_min = evaluate_employee_count_criterion(company_min, sample_icp, 25.0)
    assert result_min.status == "match"
    
    # At maximum
    company_max = CompanyResponse(
        **{**sample_company.model_dump(), "employee_count": 1000}
    )
    result_max = evaluate_employee_count_criterion(company_max, sample_icp, 25.0)
    assert result_max.status == "match"


def test_evaluate_required_keywords_match(sample_company, sample_sources, sample_icp):
    """Test required keywords criterion - match."""
    result = evaluate_required_keywords_criterion(
        sample_company, sample_sources, sample_icp, 30.0
    )
    
    assert result.status == "match"
    assert len(result.observed_value) > 0
    assert len(result.evidence_references) > 0


def test_evaluate_required_keywords_mismatch(sample_company, sample_icp):
    """Test required keywords criterion - mismatch (no keywords found)."""
    company = CompanyResponse(
        **{**sample_company.model_dump(), "description": "A simple software tool"}
    )
    
    result = evaluate_required_keywords_criterion(
        company, [], sample_icp, 30.0
    )
    
    assert result.status == "mismatch"


def test_evaluate_required_keywords_insufficient_evidence(sample_icp):
    """Test required keywords criterion - insufficient evidence."""
    company = CompanyResponse(
        id="507f1f77bcf86cd799439011",
        company_name="Test Company",
        website=None,
        industry=None,
        description=None,  # No description
        headquarters_country=None,
        headquarters_region=None,
        employee_count=None,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    
    result = evaluate_required_keywords_criterion(
        company, [], sample_icp, 30.0
    )
    
    assert result.status == "insufficient_evidence"


def test_evaluate_excluded_keywords_match(sample_company, sample_sources, sample_icp):
    """Test excluded keywords criterion - match (no excluded keywords found)."""
    result = evaluate_excluded_keywords_criterion(
        sample_company, sample_sources, sample_icp, 10.0
    )
    
    assert result.status == "match"


def test_evaluate_excluded_keywords_mismatch(sample_company, sample_icp):
    """Test excluded keywords criterion - mismatch (excluded keyword found)."""
    company = CompanyResponse(
        **{**sample_company.model_dump(), "description": "Consumer-focused B2C platform"}
    )
    
    result = evaluate_excluded_keywords_criterion(
        company, [], sample_icp, 10.0
    )
    
    assert result.status == "mismatch"
    assert len(result.observed_value) > 0


def test_calculate_score_all_match():
    """Test score calculation when all criteria match."""
    from app.models.qualification import CriterionEvaluation
    
    evaluations = [
        CriterionEvaluation(
            criterion_id="test1",
            criterion_name="Test 1",
            weight=50.0,
            status="match",
            explanation="Match",
            observed_value=None,
            expected_value=None
        ),
        CriterionEvaluation(
            criterion_id="test2",
            criterion_name="Test 2",
            weight=50.0,
            status="match",
            explanation="Match",
            observed_value=None,
            expected_value=None
        )
    ]
    
    icp = ICPResponse(
        id="test",
        name="Test",
        description=None,
        industries=None,
        headquarters_countries=None,
        minimum_employee_count=None,
        maximum_employee_count=None,
        required_keywords=None,
        excluded_keywords=None,
        criteria_weights={"test1": 50.0, "test2": 50.0},
        qualification_threshold=70.0,
        partial_qualification_threshold=50.0,
        minimum_evidence_coverage=60.0,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    
    score, coverage = calculate_score_and_coverage(evaluations, icp)
    
    assert score == 100.0
    assert coverage == 100.0


def test_calculate_score_partial_match():
    """Test score calculation with partial match."""
    from app.models.qualification import CriterionEvaluation
    
    evaluations = [
        CriterionEvaluation(
            criterion_id="test1",
            criterion_name="Test 1",
            weight=50.0,
            status="match",
            explanation="Match",
            observed_value=None,
            expected_value=None
        ),
        CriterionEvaluation(
            criterion_id="test2",
            criterion_name="Test 2",
            weight=50.0,
            status="mismatch",
            explanation="Mismatch",
            observed_value=None,
            expected_value=None
        )
    ]
    
    icp = ICPResponse(
        id="test",
        name="Test",
        description=None,
        industries=None,
        headquarters_countries=None,
        minimum_employee_count=None,
        maximum_employee_count=None,
        required_keywords=None,
        excluded_keywords=None,
        criteria_weights={"test1": 50.0, "test2": 50.0},
        qualification_threshold=70.0,
        partial_qualification_threshold=50.0,
        minimum_evidence_coverage=60.0,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    
    score, coverage = calculate_score_and_coverage(evaluations, icp)
    
    assert score == 50.0
    assert coverage == 100.0


def test_calculate_score_insufficient_evidence():
    """Test score calculation with insufficient evidence."""
    from app.models.qualification import CriterionEvaluation
    
    evaluations = [
        CriterionEvaluation(
            criterion_id="test1",
            criterion_name="Test 1",
            weight=50.0,
            status="match",
            explanation="Match",
            observed_value=None,
            expected_value=None
        ),
        CriterionEvaluation(
            criterion_id="test2",
            criterion_name="Test 2",
            weight=50.0,
            status="insufficient_evidence",
            explanation="Insufficient",
            observed_value=None,
            expected_value=None
        )
    ]
    
    icp = ICPResponse(
        id="test",
        name="Test",
        description=None,
        industries=None,
        headquarters_countries=None,
        minimum_employee_count=None,
        maximum_employee_count=None,
        required_keywords=None,
        excluded_keywords=None,
        criteria_weights={"test1": 50.0, "test2": 50.0},
        qualification_threshold=70.0,
        partial_qualification_threshold=50.0,
        minimum_evidence_coverage=60.0,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    
    score, coverage = calculate_score_and_coverage(evaluations, icp)
    
    # Score based only on evaluable criteria
    assert score == 100.0  # Only test1 is evaluable, and it matches
    # Coverage is 50% (only 50 out of 100 weight could be evaluated)
    assert coverage == 50.0


def test_calculate_score_zero_evaluable_weight():
    """Test score calculation with zero evaluable weight."""
    from app.models.qualification import CriterionEvaluation
    
    evaluations = [
        CriterionEvaluation(
            criterion_id="test1",
            criterion_name="Test 1",
            weight=50.0,
            status="insufficient_evidence",
            explanation="Insufficient",
            observed_value=None,
            expected_value=None
        )
    ]
    
    icp = ICPResponse(
        id="test",
        name="Test",
        description=None,
        industries=None,
        headquarters_countries=None,
        minimum_employee_count=None,
        maximum_employee_count=None,
        required_keywords=None,
        excluded_keywords=None,
        criteria_weights={"test1": 50.0},
        qualification_threshold=70.0,
        partial_qualification_threshold=50.0,
        minimum_evidence_coverage=60.0,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    
    score, coverage = calculate_score_and_coverage(evaluations, icp)
    
    assert score is None
    assert coverage == 0.0


def test_determine_outcome_qualified(sample_icp):
    """Test outcome determination - qualified."""
    from app.models.qualification import CriterionEvaluation
    
    evaluations = []
    score = 80.0
    coverage = 90.0
    
    outcome, explanation = determine_outcome(score, coverage, evaluations, sample_icp)
    
    assert outcome == "qualified"


def test_determine_outcome_partially_qualified(sample_icp):
    """Test outcome determination - partially qualified."""
    evaluations = []
    score = 60.0  # Between partial (50) and full (70) thresholds
    coverage = 90.0
    
    outcome, explanation = determine_outcome(score, coverage, evaluations, sample_icp)
    
    assert outcome == "partially_qualified"


def test_determine_outcome_not_qualified(sample_icp):
    """Test outcome determination - not qualified."""
    evaluations = []
    score = 40.0  # Below partial threshold (50)
    coverage = 90.0
    
    outcome, explanation = determine_outcome(score, coverage, evaluations, sample_icp)
    
    assert outcome == "not_qualified"


def test_determine_outcome_insufficient_data_no_score(sample_icp):
    """Test outcome determination - insufficient data (no score)."""
    evaluations = []
    score = None
    coverage = None
    
    outcome, explanation = determine_outcome(score, coverage, evaluations, sample_icp)
    
    assert outcome == "insufficient_data"


def test_determine_outcome_insufficient_coverage(sample_icp):
    """Test outcome determination - insufficient coverage."""
    evaluations = []
    score = 80.0  # High score
    coverage = 40.0  # Low coverage (below 60% minimum)
    
    outcome, explanation = determine_outcome(score, coverage, evaluations, sample_icp)
    
    assert outcome == "insufficient_data"


def test_determine_outcome_excluded_keyword_disqualifies(sample_icp):
    """Test outcome determination - excluded keyword disqualifies."""
    from app.models.qualification import CriterionEvaluation
    
    evaluations = [
        CriterionEvaluation(
            criterion_id="excluded_keywords",
            criterion_name="Excluded Keywords",
            weight=10.0,
            status="mismatch",
            explanation="Found excluded keyword: consumer",
            observed_value=["consumer"],
            expected_value=["consumer", "B2C"]
        )
    ]
    score = 80.0  # High score, but excluded keyword found
    coverage = 90.0
    
    outcome, explanation = determine_outcome(score, coverage, evaluations, sample_icp)
    
    assert outcome == "not_qualified"
    assert "Disqualified" in explanation


def test_qualify_company_full_match(sample_company, sample_sources, sample_icp):
    """Test full company qualification with all criteria matching."""
    score, coverage, outcome, explanation, evaluations, limitations = qualify_company(
        sample_company, sample_sources, sample_icp
    )
    
    assert score is not None
    assert coverage is not None
    assert outcome in ["qualified", "partially_qualified", "not_qualified", "insufficient_data"]
    assert len(evaluations) == 5  # All 5 criteria evaluated
    assert limitations is not None
