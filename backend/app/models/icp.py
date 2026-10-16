"""ICP (Ideal Customer Profile) data models."""
from datetime import datetime
from typing import Optional, Dict
from pydantic import BaseModel, Field, field_validator, ConfigDict


class ICPCreate(BaseModel):
    """Schema for creating a new ICP."""
    
    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="ICP name (required)"
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="ICP description"
    )
    industries: Optional[list[str]] = Field(
        None,
        max_length=50,
        description="Accepted industry values (case-insensitive matching)"
    )
    headquarters_countries: Optional[list[str]] = Field(
        None,
        max_length=50,
        description="Accepted headquarters countries (case-insensitive matching)"
    )
    minimum_employee_count: Optional[int] = Field(
        None,
        ge=0,
        description="Minimum employee count (inclusive)"
    )
    maximum_employee_count: Optional[int] = Field(
        None,
        ge=0,
        description="Maximum employee count (inclusive)"
    )
    required_keywords: Optional[list[str]] = Field(
        None,
        max_length=50,
        description="Keywords that must be present (case-insensitive)"
    )
    excluded_keywords: Optional[list[str]] = Field(
        None,
        max_length=50,
        description="Keywords that disqualify if present (case-insensitive)"
    )
    criteria_weights: Dict[str, float] = Field(
        default_factory=lambda: {
            "industry": 20.0,
            "headquarters_country": 15.0,
            "employee_count": 25.0,
            "required_keywords": 30.0,
            "excluded_keywords": 10.0
        },
        description="Weight for each criterion (must be non-negative)"
    )
    qualification_threshold: float = Field(
        70.0,
        ge=0.0,
        le=100.0,
        description="Minimum score to be considered qualified"
    )
    partial_qualification_threshold: float = Field(
        50.0,
        ge=0.0,
        le=100.0,
        description="Minimum score for partial qualification"
    )
    minimum_evidence_coverage: float = Field(
        60.0,
        ge=0.0,
        le=100.0,
        description="Minimum evidence coverage required for qualification"
    )
    
    @field_validator('name')
    @classmethod
    def normalize_name(cls, v: str) -> str:
        """Normalize ICP name by trimming and collapsing whitespace."""
        if not v or not v.strip():
            raise ValueError('ICP name cannot be empty or whitespace only')
        return ' '.join(v.split())
    
    @field_validator('description')
    @classmethod
    def normalize_description(cls, v: Optional[str]) -> Optional[str]:
        """Normalize description."""
        if v is None:
            return None
        stripped = v.strip()
        return stripped if stripped else None
    
    @field_validator('industries', 'headquarters_countries', 'required_keywords', 'excluded_keywords')
    @classmethod
    def normalize_string_lists(cls, v: Optional[list[str]]) -> Optional[list[str]]:
        """Normalize and validate string lists."""
        if v is None:
            return None
        # Remove empty strings and trim whitespace
        normalized = [s.strip() for s in v if s and s.strip()]
        return normalized if normalized else None
    
    @field_validator('maximum_employee_count')
    @classmethod
    def validate_employee_range(cls, v: Optional[int], info) -> Optional[int]:
        """Validate that maximum is not less than minimum."""
        if v is not None and 'minimum_employee_count' in info.data:
            minimum = info.data['minimum_employee_count']
            if minimum is not None and v < minimum:
                raise ValueError(
                    f'Maximum employee count ({v}) cannot be less than minimum ({minimum})'
                )
        return v
    
    @field_validator('criteria_weights')
    @classmethod
    def validate_weights(cls, v: Dict[str, float]) -> Dict[str, float]:
        """Validate that all weights are non-negative."""
        for key, weight in v.items():
            if weight < 0:
                raise ValueError(f'Weight for {key} cannot be negative: {weight}')
        return v
    
    @field_validator('partial_qualification_threshold')
    @classmethod
    def validate_thresholds(cls, v: float, info) -> float:
        """Validate that partial threshold is not greater than qualification threshold."""
        if 'qualification_threshold' in info.data:
            qual_threshold = info.data['qualification_threshold']
            if v > qual_threshold:
                raise ValueError(
                    f'Partial qualification threshold ({v}) cannot be greater than '
                    f'qualification threshold ({qual_threshold})'
                )
        return v


class ICPUpdate(BaseModel):
    """Schema for updating an existing ICP."""
    
    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=200,
        description="ICP name"
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="ICP description"
    )
    industries: Optional[list[str]] = Field(
        None,
        max_length=50,
        description="Accepted industry values"
    )
    headquarters_countries: Optional[list[str]] = Field(
        None,
        max_length=50,
        description="Accepted headquarters countries"
    )
    minimum_employee_count: Optional[int] = Field(
        None,
        ge=0,
        description="Minimum employee count"
    )
    maximum_employee_count: Optional[int] = Field(
        None,
        ge=0,
        description="Maximum employee count"
    )
    required_keywords: Optional[list[str]] = Field(
        None,
        max_length=50,
        description="Required keywords"
    )
    excluded_keywords: Optional[list[str]] = Field(
        None,
        max_length=50,
        description="Excluded keywords"
    )
    criteria_weights: Optional[Dict[str, float]] = Field(
        None,
        description="Criterion weights"
    )
    qualification_threshold: Optional[float] = Field(
        None,
        ge=0.0,
        le=100.0,
        description="Qualification threshold"
    )
    partial_qualification_threshold: Optional[float] = Field(
        None,
        ge=0.0,
        le=100.0,
        description="Partial qualification threshold"
    )
    minimum_evidence_coverage: Optional[float] = Field(
        None,
        ge=0.0,
        le=100.0,
        description="Minimum evidence coverage"
    )
    
    @field_validator('name')
    @classmethod
    def normalize_name(cls, v: Optional[str]) -> Optional[str]:
        """Normalize ICP name."""
        if v is None:
            return None
        if not v.strip():
            raise ValueError('ICP name cannot be empty or whitespace only')
        return ' '.join(v.split())
    
    @field_validator('description')
    @classmethod
    def normalize_description(cls, v: Optional[str]) -> Optional[str]:
        """Normalize description."""
        if v is None:
            return None
        stripped = v.strip()
        return stripped if stripped else None
    
    @field_validator('industries', 'headquarters_countries', 'required_keywords', 'excluded_keywords')
    @classmethod
    def normalize_string_lists(cls, v: Optional[list[str]]) -> Optional[list[str]]:
        """Normalize string lists."""
        if v is None:
            return None
        normalized = [s.strip() for s in v if s and s.strip()]
        return normalized if normalized else None
    
    @field_validator('criteria_weights')
    @classmethod
    def validate_weights(cls, v: Optional[Dict[str, float]]) -> Optional[Dict[str, float]]:
        """Validate weights."""
        if v is None:
            return None
        for key, weight in v.items():
            if weight < 0:
                raise ValueError(f'Weight for {key} cannot be negative: {weight}')
        return v


class ICPResponse(BaseModel):
    """Schema for ICP responses."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: str = Field(..., description="ICP ID")
    name: str = Field(..., description="ICP name")
    description: Optional[str] = Field(None, description="ICP description")
    industries: Optional[list[str]] = Field(None, description="Accepted industries")
    headquarters_countries: Optional[list[str]] = Field(None, description="Accepted countries")
    minimum_employee_count: Optional[int] = Field(None, description="Minimum employee count")
    maximum_employee_count: Optional[int] = Field(None, description="Maximum employee count")
    required_keywords: Optional[list[str]] = Field(None, description="Required keywords")
    excluded_keywords: Optional[list[str]] = Field(None, description="Excluded keywords")
    criteria_weights: Dict[str, float] = Field(..., description="Criterion weights")
    qualification_threshold: float = Field(..., description="Qualification threshold")
    partial_qualification_threshold: float = Field(..., description="Partial qualification threshold")
    minimum_evidence_coverage: float = Field(..., description="Minimum evidence coverage")
    created_at: datetime = Field(..., description="Creation timestamp (UTC)")
    updated_at: datetime = Field(..., description="Last update timestamp (UTC)")


class ICPListResponse(BaseModel):
    """Schema for paginated ICP list responses."""
    
    items: list[ICPResponse] = Field(..., description="List of ICPs")
    total: int = Field(..., description="Total number of ICPs")
    limit: int = Field(..., description="Page size limit")
    offset: int = Field(..., description="Page offset")
