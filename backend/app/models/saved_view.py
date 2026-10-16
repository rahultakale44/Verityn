"""Saved view data models for lead intelligence."""
from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, field_validator, ConfigDict


# Re-export sort types for convenience
SortField = Literal["score", "evidence_coverage", "qualified_at", "outcome"]
SortDirection = Literal["asc", "desc"]


class SavedViewFilters(BaseModel):
    """
    Filter configuration for a saved view.
    
    Stores the filter criteria that can be applied to lead searches.
    When a saved view is loaded, these filters are applied to the current data.
    """
    
    # Required filter
    icp_id: str = Field(..., description="ICP ID to filter leads by")
    
    # Qualification outcome filters
    outcomes: Optional[List[str]] = Field(
        None,
        description="Qualification outcomes to include (qualified, partially_qualified, not_qualified, insufficient_data)"
    )
    
    # Score filters
    min_score: Optional[float] = Field(
        None,
        ge=0.0,
        le=100.0,
        description="Minimum qualification score"
    )
    max_score: Optional[float] = Field(
        None,
        ge=0.0,
        le=100.0,
        description="Maximum qualification score"
    )
    
    # Evidence coverage filter
    min_evidence_coverage: Optional[float] = Field(
        None,
        ge=0.0,
        le=100.0,
        description="Minimum evidence coverage percentage"
    )
    
    # Company attribute filters
    industries: Optional[List[str]] = Field(
        None,
        description="Company industries to include"
    )
    countries: Optional[List[str]] = Field(
        None,
        description="Company headquarters countries to include"
    )
    
    # Employee count range
    min_employees: Optional[int] = Field(
        None,
        ge=0,
        description="Minimum employee count"
    )
    max_employees: Optional[int] = Field(
        None,
        ge=0,
        description="Maximum employee count"
    )
    
    # Company name search
    company_name_search: Optional[str] = Field(
        None,
        max_length=200,
        description="Company name search term (case-insensitive partial match)"
    )
    
    # Research availability filter
    has_research: Optional[bool] = Field(
        None,
        description="Filter by research availability (true=has research, false=no research, null=no filter)"
    )
    
    # Sorting
    sort_by: SortField = Field(
        "score",
        description="Field to sort by"
    )
    sort_direction: SortDirection = Field(
        "desc",
        description="Sort direction"
    )
    
    @field_validator('outcomes')
    @classmethod
    def validate_outcomes(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate outcome values."""
        if v is None:
            return None
        
        valid_outcomes = {"qualified", "partially_qualified", "not_qualified", "insufficient_data"}
        for outcome in v:
            if outcome not in valid_outcomes:
                raise ValueError(f"Invalid outcome: {outcome}. Must be one of {valid_outcomes}")
        
        # Remove duplicates
        return list(set(v)) if v else None
    
    @field_validator('max_score')
    @classmethod
    def validate_score_range(cls, v: Optional[float], info) -> Optional[float]:
        """Validate that max_score is not less than min_score."""
        if v is not None and 'min_score' in info.data:
            min_score = info.data['min_score']
            if min_score is not None and v < min_score:
                raise ValueError(f"max_score ({v}) cannot be less than min_score ({min_score})")
        return v
    
    @field_validator('max_employees')
    @classmethod
    def validate_employee_range(cls, v: Optional[int], info) -> Optional[int]:
        """Validate that max_employees is not less than min_employees."""
        if v is not None and 'min_employees' in info.data:
            min_employees = info.data['min_employees']
            if min_employees is not None and v < min_employees:
                raise ValueError(f"max_employees ({v}) cannot be less than min_employees ({min_employees})")
        return v
    
    @field_validator('industries', 'countries')
    @classmethod
    def normalize_string_lists(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Normalize and validate string lists."""
        if v is None:
            return None
        # Remove empty strings, trim whitespace, remove duplicates
        normalized = list(set([s.strip() for s in v if s and s.strip()]))
        return normalized if normalized else None
    
    @field_validator('company_name_search')
    @classmethod
    def normalize_search_term(cls, v: Optional[str]) -> Optional[str]:
        """Normalize search term."""
        if v is None:
            return None
        stripped = v.strip()
        return stripped if stripped else None


class SavedViewCreate(BaseModel):
    """Schema for creating a new saved view."""
    
    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Saved view name (required)"
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Saved view description"
    )
    filters: SavedViewFilters = Field(
        ...,
        description="Filter configuration"
    )
    
    @field_validator('name')
    @classmethod
    def normalize_name(cls, v: str) -> str:
        """Normalize view name."""
        if not v or not v.strip():
            raise ValueError('Saved view name cannot be empty or whitespace only')
        return ' '.join(v.split())
    
    @field_validator('description')
    @classmethod
    def normalize_description(cls, v: Optional[str]) -> Optional[str]:
        """Normalize description."""
        if v is None:
            return None
        stripped = v.strip()
        return stripped if stripped else None


class SavedViewUpdate(BaseModel):
    """Schema for updating an existing saved view."""
    
    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=200,
        description="Saved view name"
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Saved view description"
    )
    filters: Optional[SavedViewFilters] = Field(
        None,
        description="Filter configuration"
    )
    
    @field_validator('name')
    @classmethod
    def normalize_name(cls, v: Optional[str]) -> Optional[str]:
        """Normalize view name."""
        if v is None:
            return None
        if not v.strip():
            raise ValueError('Saved view name cannot be empty or whitespace only')
        return ' '.join(v.split())
    
    @field_validator('description')
    @classmethod
    def normalize_description(cls, v: Optional[str]) -> Optional[str]:
        """Normalize description."""
        if v is None:
            return None
        stripped = v.strip()
        return stripped if stripped else None


class SavedViewResponse(BaseModel):
    """Schema for saved view responses."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: str = Field(..., description="Saved view ID")
    name: str = Field(..., description="Saved view name")
    description: Optional[str] = Field(None, description="Saved view description")
    filters: SavedViewFilters = Field(..., description="Filter configuration")
    created_at: datetime = Field(..., description="Creation timestamp (UTC)")
    updated_at: datetime = Field(..., description="Last update timestamp (UTC)")


class SavedViewListResponse(BaseModel):
    """Schema for paginated saved view list responses."""
    
    items: list[SavedViewResponse] = Field(..., description="List of saved views")
    total: int = Field(..., description="Total number of saved views")
    limit: int = Field(..., description="Page size limit")
    offset: int = Field(..., description="Page offset")
