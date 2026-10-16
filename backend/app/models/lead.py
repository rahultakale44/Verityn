"""Lead intelligence data models."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.models.qualification import QualificationOutcome


class LeadResponse(BaseModel):
    """
    Combined company and qualification information for lead intelligence.
    
    Represents a company along with its latest qualification result against an ICP.
    """
    
    model_config = ConfigDict(from_attributes=True)
    
    # Company information
    company_id: str = Field(..., description="Company ID")
    company_name: str = Field(..., description="Company name")
    website: Optional[str] = Field(None, description="Company website URL")
    industry: Optional[str] = Field(None, description="Industry sector")
    headquarters_country: Optional[str] = Field(None, description="Headquarters country")
    headquarters_region: Optional[str] = Field(None, description="Headquarters region/state")
    employee_count: Optional[int] = Field(None, description="Number of employees")
    
    # Qualification information
    qualification_id: str = Field(..., description="Qualification ID")
    icp_id: str = Field(..., description="ICP ID used for qualification")
    icp_name: str = Field(..., description="ICP name")
    qualified_at: datetime = Field(..., description="Qualification timestamp (UTC)")
    score: Optional[float] = Field(None, description="Qualification score (0-100)")
    evidence_coverage: Optional[float] = Field(None, description="Evidence coverage percentage (0-100)")
    outcome: QualificationOutcome = Field(..., description="Qualification outcome")
    outcome_explanation: str = Field(..., description="Explanation of the outcome")
    
    # Research availability
    has_research: bool = Field(..., description="Whether research data exists for this company")


class LeadListResponse(BaseModel):
    """Schema for paginated lead list responses."""
    
    items: list[LeadResponse] = Field(..., description="List of leads")
    total: int = Field(..., description="Total number of leads matching filters")
    limit: int = Field(..., description="Page size limit")
    offset: int = Field(..., description="Page offset")
    sort_by: str = Field(..., description="Field used for sorting")
    sort_direction: str = Field(..., description="Sort direction (asc or desc)")
