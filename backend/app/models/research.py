"""Research data models."""
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict


# Research run status types
ResearchStatus = Literal["pending", "running", "completed", "partial", "failed"]


class ResearchRunResponse(BaseModel):
    """Schema for research run responses."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: str = Field(..., description="Research run ID")
    company_id: str = Field(..., description="Associated company ID")
    status: ResearchStatus = Field(..., description="Current status of the research run")
    started_at: datetime = Field(..., description="When the research run started (UTC)")
    completed_at: Optional[datetime] = Field(None, description="When the research run completed (UTC)")
    queries_executed: int = Field(..., description="Number of search queries executed")
    sources_found: int = Field(..., description="Total sources found from searches")
    sources_saved: int = Field(..., description="Number of sources successfully saved")
    error_summary: Optional[str] = Field(None, description="Error summary if applicable")


class ResearchRunListResponse(BaseModel):
    """Schema for paginated research run list responses."""
    
    items: list[ResearchRunResponse] = Field(..., description="List of research runs")
    total: int = Field(..., description="Total number of research runs")
    limit: int = Field(..., description="Page size limit")
    offset: int = Field(..., description="Page offset")


class SourceEvidenceResponse(BaseModel):
    """Schema for source evidence responses."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: str = Field(..., description="Source evidence ID")
    research_run_id: str = Field(..., description="Associated research run ID")
    company_id: str = Field(..., description="Associated company ID")
    source_url: str = Field(..., description="Original source URL")
    source_domain: str = Field(..., description="Source domain")
    title: str = Field(..., description="Source title")
    snippet: str = Field(..., description="Content snippet")
    published_at: Optional[datetime] = Field(None, description="Publication date (if provided)")
    retrieved_at: datetime = Field(..., description="When the source was retrieved (UTC)")
    provider: str = Field(..., description="Search provider (e.g., Tavily)")
    content_type: Optional[str] = Field(None, description="Content type or category")


class SourceEvidenceListResponse(BaseModel):
    """Schema for paginated source evidence list responses."""
    
    items: list[SourceEvidenceResponse] = Field(..., description="List of source evidence")
    total: int = Field(..., description="Total number of sources")
    limit: int = Field(..., description="Page size limit")
    offset: int = Field(..., description="Page offset")
