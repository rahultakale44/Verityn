"""Qualification data models."""
from datetime import datetime
from typing import Optional, Literal, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict


# Criterion evaluation status
CriterionStatus = Literal["match", "mismatch", "insufficient_evidence", "not_applicable"]

# Qualification outcome
QualificationOutcome = Literal["qualified", "partially_qualified", "not_qualified", "insufficient_data"]


class EvidenceReference(BaseModel):
    """Reference to a source evidence record."""
    
    source_id: str = Field(..., description="Source evidence ID")
    source_url: str = Field(..., description="Source URL")
    title: str = Field(..., description="Source title")
    snippet: str = Field(..., description="Relevant snippet")


class CriterionEvaluation(BaseModel):
    """Evaluation result for a single criterion."""
    
    criterion_id: str = Field(..., description="Criterion identifier")
    criterion_name: str = Field(..., description="Human-readable criterion name")
    weight: float = Field(..., description="Configured weight for this criterion")
    status: CriterionStatus = Field(..., description="Evaluation status")
    explanation: str = Field(..., description="Concise explanation of the evaluation")
    observed_value: Optional[Any] = Field(None, description="Observed value from company data")
    expected_value: Optional[Any] = Field(None, description="Expected value from ICP configuration")
    evidence_references: list[EvidenceReference] = Field(
        default_factory=list,
        description="References to supporting evidence"
    )
    reason_insufficient: Optional[str] = Field(
        None,
        description="Reason for insufficient evidence, if applicable"
    )


class QualificationRequest(BaseModel):
    """Request to qualify a company against an ICP."""
    
    icp_id: str = Field(..., description="ICP ID to use for qualification")


class QualificationResponse(BaseModel):
    """Schema for qualification result responses."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: str = Field(..., description="Qualification run ID")
    company_id: str = Field(..., description="Company ID")
    icp_id: str = Field(..., description="ICP ID used")
    icp_snapshot: Dict[str, Any] = Field(..., description="Immutable snapshot of ICP configuration")
    qualified_at: datetime = Field(..., description="Qualification timestamp (UTC)")
    score: Optional[float] = Field(None, description="Qualification score (0-100)")
    evidence_coverage: Optional[float] = Field(None, description="Evidence coverage percentage (0-100)")
    outcome: QualificationOutcome = Field(..., description="Qualification outcome")
    outcome_explanation: str = Field(..., description="Explanation of the outcome")
    criteria_evaluations: list[CriterionEvaluation] = Field(
        ...,
        description="Detailed evaluation of each criterion"
    )
    limitations: Optional[str] = Field(None, description="Known limitations of this qualification")


class QualificationListResponse(BaseModel):
    """Schema for paginated qualification list responses."""
    
    items: list[QualificationResponse] = Field(..., description="List of qualification results")
    total: int = Field(..., description="Total number of qualification results")
    limit: int = Field(..., description="Page size limit")
    offset: int = Field(..., description="Page offset")
