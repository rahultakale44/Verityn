"""Tests for ranking engine service."""
from datetime import datetime, timezone, timedelta
from app.services.ranking_engine import (
    rank_leads,
    get_latest_qualifications_per_company,
    get_latest_qualification_for_icp,
    get_sort_key_for_outcome
)
from app.models.qualification import QualificationResponse, CriterionEvaluation


def create_test_qualification(
    qual_id: str,
    company_id: str,
    icp_id: str,
    score: float = None,
    evidence_coverage: float = None,
    outcome: str = "qualified",
    qualified_at: datetime = None
) -> QualificationResponse:
    """Helper to create test qualification."""
    if qualified_at is None:
        qualified_at = datetime.now(timezone.utc)
    
    return QualificationResponse(
        id=qual_id,
        company_id=company_id,
        icp_id=icp_id,
        icp_snapshot={"name": "Test ICP"},
        qualified_at=qualified_at,
        score=score,
        evidence_coverage=evidence_coverage,
        outcome=outcome,
        outcome_explanation="Test explanation",
        criteria_evaluations=[]
    )


def test_rank_by_score_descending():
    """Test ranking by score descending (highest first)."""
    now = datetime.now(timezone.utc)
    quals = [
        create_test_qualification("1", "c1", "i1", score=85.0, qualified_at=now),
        create_test_qualification("2", "c2", "i1", score=95.0, qualified_at=now),
        create_test_qualification("3", "c3", "i1", score=75.0, qualified_at=now),
    ]
    
    ranked = rank_leads(quals, "score", "desc")
    
    assert len(ranked) == 3
    assert ranked[0].id == "2"  # 95.0
    assert ranked[1].id == "1"  # 85.0
    assert ranked[2].id == "3"  # 75.0


def test_rank_by_score_ascending():
    """Test ranking by score ascending (lowest first)."""
    now = datetime.now(timezone.utc)
    quals = [
        create_test_qualification("1", "c1", "i1", score=85.0, qualified_at=now),
        create_test_qualification("2", "c2", "i1", score=95.0, qualified_at=now),
        create_test_qualification("3", "c3", "i1", score=75.0, qualified_at=now),
    ]
    
    ranked = rank_leads(quals, "score", "asc")
    
    assert len(ranked) == 3
    assert ranked[0].id == "3"  # 75.0
    assert ranked[1].id == "1"  # 85.0
    assert ranked[2].id == "2"  # 95.0


def test_rank_with_none_scores():
    """Test that None scores are sorted to end regardless of direction."""
    now = datetime.now(timezone.utc)
    quals = [
        create_test_qualification("1", "c1", "i1", score=85.0, qualified_at=now),
        create_test_qualification("2", "c2", "i1", score=None, qualified_at=now),
        create_test_qualification("3", "c3", "i1", score=75.0, qualified_at=now),
    ]
    
    # Descending: None should be last
    ranked_desc = rank_leads(quals, "score", "desc")
    assert ranked_desc[2].id == "2"  # None at end
    
    # Ascending: None should still be last
    ranked_asc = rank_leads(quals, "score", "asc")
    assert ranked_asc[2].id == "2"  # None at end


def test_rank_by_evidence_coverage():
    """Test ranking by evidence coverage."""
    now = datetime.now(timezone.utc)
    quals = [
        create_test_qualification("1", "c1", "i1", evidence_coverage=80.0, qualified_at=now),
        create_test_qualification("2", "c2", "i1", evidence_coverage=90.0, qualified_at=now),
        create_test_qualification("3", "c3", "i1", evidence_coverage=70.0, qualified_at=now),
    ]
    
    ranked = rank_leads(quals, "evidence_coverage", "desc")
    
    assert ranked[0].id == "2"  # 90.0
    assert ranked[1].id == "1"  # 80.0
    assert ranked[2].id == "3"  # 70.0


def test_rank_by_outcome():
    """Test ranking by outcome quality."""
    now = datetime.now(timezone.utc)
    quals = [
        create_test_qualification("1", "c1", "i1", outcome="not_qualified", qualified_at=now),
        create_test_qualification("2", "c2", "i1", outcome="qualified", qualified_at=now),
        create_test_qualification("3", "c3", "i1", outcome="partially_qualified", qualified_at=now),
        create_test_qualification("4", "c4", "i1", outcome="insufficient_data", qualified_at=now),
    ]
    
    ranked = rank_leads(quals, "outcome", "desc")
    
    # Outcome rank: qualified(1) > partially_qualified(2) > not_qualified(3) > insufficient_data(4)
    assert ranked[0].id == "2"  # qualified
    assert ranked[1].id == "3"  # partially_qualified
    assert ranked[2].id == "1"  # not_qualified
    assert ranked[3].id == "4"  # insufficient_data


def test_rank_by_qualified_at():
    """Test ranking by qualified_at timestamp."""
    now = datetime.now(timezone.utc)
    quals = [
        create_test_qualification("1", "c1", "i1", qualified_at=now - timedelta(days=2)),
        create_test_qualification("2", "c2", "i1", qualified_at=now - timedelta(days=1)),
        create_test_qualification("3", "c3", "i1", qualified_at=now),
    ]
    
    ranked = rank_leads(quals, "qualified_at", "desc")
    
    assert ranked[0].id == "3"  # most recent
    assert ranked[1].id == "2"
    assert ranked[2].id == "1"  # oldest


def test_tie_breaking_by_timestamp():
    """Test tie-breaking with qualified_at when scores are equal."""
    now = datetime.now(timezone.utc)
    quals = [
        create_test_qualification("1", "c1", "i1", score=85.0, qualified_at=now - timedelta(hours=1)),
        create_test_qualification("2", "c2", "i1", score=85.0, qualified_at=now),
        create_test_qualification("3", "c3", "i1", score=85.0, qualified_at=now - timedelta(hours=2)),
    ]
    
    ranked = rank_leads(quals, "score", "desc")
    
    # Same score, so should be ordered by qualified_at desc (newer first)
    assert ranked[0].id == "2"  # most recent
    assert ranked[1].id == "1"
    assert ranked[2].id == "3"  # oldest


def test_tie_breaking_by_id():
    """Test final tie-breaking with ID when scores and timestamps are equal."""
    now = datetime.now(timezone.utc)
    quals = [
        create_test_qualification("c", "c3", "i1", score=85.0, qualified_at=now),
        create_test_qualification("a", "c1", "i1", score=85.0, qualified_at=now),
        create_test_qualification("b", "c2", "i1", score=85.0, qualified_at=now),
    ]
    
    ranked = rank_leads(quals, "score", "desc")
    
    # Same score and timestamp, so should be ordered by ID asc (a < b < c)
    assert ranked[0].id == "a"
    assert ranked[1].id == "b"
    assert ranked[2].id == "c"


def test_rank_empty_list():
    """Test ranking empty list."""
    ranked = rank_leads([], "score", "desc")
    assert ranked == []


def test_get_latest_qualifications_per_company():
    """Test getting latest qualification per company."""
    now = datetime.now(timezone.utc)
    quals = [
        create_test_qualification("1", "c1", "i1", qualified_at=now - timedelta(days=1)),
        create_test_qualification("2", "c1", "i1", qualified_at=now),  # Latest for c1
        create_test_qualification("3", "c2", "i1", qualified_at=now - timedelta(days=2)),
        create_test_qualification("4", "c2", "i1", qualified_at=now - timedelta(days=1)),  # Latest for c2
    ]
    
    latest = get_latest_qualifications_per_company(quals)
    
    assert len(latest) == 2
    assert latest["c1"].id == "2"
    assert latest["c2"].id == "4"


def test_get_latest_with_same_timestamp():
    """Test latest qualification selection with same timestamp uses ID tie-break."""
    now = datetime.now(timezone.utc)
    quals = [
        create_test_qualification("b", "c1", "i1", qualified_at=now),
        create_test_qualification("a", "c1", "i1", qualified_at=now),  # Should win (ID asc)
        create_test_qualification("c", "c1", "i1", qualified_at=now),
    ]
    
    latest = get_latest_qualifications_per_company(quals)
    
    assert len(latest) == 1
    assert latest["c1"].id == "a"  # ID tie-break


def test_get_latest_qualification_for_icp():
    """Test getting latest qualification per company for specific ICP."""
    now = datetime.now(timezone.utc)
    quals = [
        create_test_qualification("1", "c1", "i1", qualified_at=now - timedelta(days=1)),
        create_test_qualification("2", "c1", "i1", qualified_at=now),  # Latest for c1, icp i1
        create_test_qualification("3", "c1", "i2", qualified_at=now),  # Different ICP
        create_test_qualification("4", "c2", "i1", qualified_at=now),  # Latest for c2, icp i1
    ]
    
    latest = get_latest_qualification_for_icp(quals, "i1")
    
    assert len(latest) == 2
    assert latest["c1"].id == "2"
    assert latest["c2"].id == "4"
    
    # ICP i2 should only have c1
    latest_i2 = get_latest_qualification_for_icp(quals, "i2")
    assert len(latest_i2) == 1
    assert latest_i2["c1"].id == "3"


def test_outcome_sort_key():
    """Test outcome ranking order."""
    assert get_sort_key_for_outcome(create_test_qualification("1", "c1", "i1", outcome="qualified")) == 1
    assert get_sort_key_for_outcome(create_test_qualification("2", "c2", "i1", outcome="partially_qualified")) == 2
    assert get_sort_key_for_outcome(create_test_qualification("3", "c3", "i1", outcome="not_qualified")) == 3
    assert get_sort_key_for_outcome(create_test_qualification("4", "c4", "i1", outcome="insufficient_data")) == 4
