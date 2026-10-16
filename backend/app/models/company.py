"""Company data models."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, HttpUrl, field_validator, ConfigDict


class CompanyCreate(BaseModel):
    """Schema for creating a new company."""
    
    company_name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Company name (required)"
    )
    website: Optional[HttpUrl] = Field(
        None,
        description="Company website URL"
    )
    industry: Optional[str] = Field(
        None,
        max_length=100,
        description="Industry sector"
    )
    description: Optional[str] = Field(
        None,
        max_length=2000,
        description="Company description"
    )
    headquarters_country: Optional[str] = Field(
        None,
        max_length=100,
        description="Headquarters country"
    )
    headquarters_region: Optional[str] = Field(
        None,
        max_length=100,
        description="Headquarters region/state"
    )
    employee_count: Optional[int] = Field(
        None,
        ge=0,
        description="Number of employees (must be non-negative)"
    )
    
    @field_validator('company_name')
    @classmethod
    def normalize_company_name(cls, v: str) -> str:
        """Normalize company name by trimming and collapsing whitespace."""
        if not v or not v.strip():
            raise ValueError('Company name cannot be empty or whitespace only')
        # Collapse multiple whitespace into single space and strip
        return ' '.join(v.split())
    
    @field_validator('industry', 'description', 'headquarters_country', 'headquarters_region')
    @classmethod
    def normalize_optional_string(cls, v: Optional[str]) -> Optional[str]:
        """Normalize optional string fields."""
        if v is None:
            return None
        stripped = v.strip()
        return stripped if stripped else None


class CompanyUpdate(BaseModel):
    """Schema for updating an existing company."""
    
    company_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=200,
        description="Company name"
    )
    website: Optional[HttpUrl] = Field(
        None,
        description="Company website URL"
    )
    industry: Optional[str] = Field(
        None,
        max_length=100,
        description="Industry sector"
    )
    description: Optional[str] = Field(
        None,
        max_length=2000,
        description="Company description"
    )
    headquarters_country: Optional[str] = Field(
        None,
        max_length=100,
        description="Headquarters country"
    )
    headquarters_region: Optional[str] = Field(
        None,
        max_length=100,
        description="Headquarters region/state"
    )
    employee_count: Optional[int] = Field(
        None,
        ge=0,
        description="Number of employees (must be non-negative)"
    )
    
    @field_validator('company_name')
    @classmethod
    def normalize_company_name(cls, v: Optional[str]) -> Optional[str]:
        """Normalize company name by trimming and collapsing whitespace."""
        if v is None:
            return None
        if not v.strip():
            raise ValueError('Company name cannot be empty or whitespace only')
        return ' '.join(v.split())
    
    @field_validator('industry', 'description', 'headquarters_country', 'headquarters_region')
    @classmethod
    def normalize_optional_string(cls, v: Optional[str]) -> Optional[str]:
        """Normalize optional string fields."""
        if v is None:
            return None
        stripped = v.strip()
        return stripped if stripped else None


class CompanyResponse(BaseModel):
    """Schema for company responses."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: str = Field(..., description="Company ID")
    company_name: str = Field(..., description="Company name")
    website: Optional[str] = Field(None, description="Company website URL")
    industry: Optional[str] = Field(None, description="Industry sector")
    description: Optional[str] = Field(None, description="Company description")
    headquarters_country: Optional[str] = Field(None, description="Headquarters country")
    headquarters_region: Optional[str] = Field(None, description="Headquarters region/state")
    employee_count: Optional[int] = Field(None, description="Number of employees")
    created_at: datetime = Field(..., description="Creation timestamp (UTC)")
    updated_at: datetime = Field(..., description="Last update timestamp (UTC)")


class CompanyListResponse(BaseModel):
    """Schema for paginated company list responses."""
    
    items: list[CompanyResponse] = Field(..., description="List of companies")
    total: int = Field(..., description="Total number of companies")
    limit: int = Field(..., description="Page size limit")
    offset: int = Field(..., description="Page offset")
