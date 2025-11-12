"""
Pydantic schemas for template service API requests and responses.
"""
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, field_validator
from shared.schemas import PaginatedResponse


class TemplateBase(BaseModel):
    """Base schema for template data."""
    name: str = Field(..., description="Template name")
    letterhead_text: Optional[str] = Field(default=None, description="Letterhead text")
    opening_paragraph: Optional[str] = Field(default=None, description="Opening paragraph text")
    closing_paragraph: Optional[str] = Field(default=None, description="Closing paragraph text")
    sections: Optional[List[str]] = Field(default=None, description="List of section names")
    is_default: bool = Field(default=False, description="Whether this is the default template for the firm")
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        """Validate template name length (1-255 characters)."""
        if not v or not v.strip():
            raise ValueError("Template name cannot be empty")
        v = v.strip()
        if len(v) > 255:
            raise ValueError("Template name cannot exceed 255 characters")
        return v
    
    @field_validator("sections")
    @classmethod
    def validate_sections(cls, v):
        """Validate section names are not empty."""
        if v is None:
            return None
        validated = []
        for section in v:
            if not section or not section.strip():
                raise ValueError("Section names cannot be empty")
            validated.append(section.strip())
        return validated


class TemplateCreate(TemplateBase):
    """Schema for template creation."""
    pass


class TemplateUpdate(BaseModel):
    """Schema for template update (all fields optional)."""
    name: Optional[str] = Field(default=None, description="Template name")
    letterhead_text: Optional[str] = Field(default=None, description="Letterhead text")
    opening_paragraph: Optional[str] = Field(default=None, description="Opening paragraph text")
    closing_paragraph: Optional[str] = Field(default=None, description="Closing paragraph text")
    sections: Optional[List[str]] = Field(default=None, description="List of section names")
    is_default: Optional[bool] = Field(default=None, description="Whether this is the default template for the firm")
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        """Validate name is not empty if provided."""
        if v is not None and (not v or not v.strip()):
            raise ValueError("Template name cannot be empty")
        if v is not None:
            v = v.strip()
            if len(v) > 255:
                raise ValueError("Template name cannot exceed 255 characters")
        return v
    
    @field_validator("sections")
    @classmethod
    def validate_sections(cls, v):
        """Validate section names are not empty if provided."""
        if v is None:
            return None
        validated = []
        for section in v:
            if not section or not section.strip():
                raise ValueError("Section names cannot be empty")
            validated.append(section.strip())
        return validated


class TemplateResponse(BaseModel):
    """Schema for template response."""
    id: UUID = Field(..., description="Template ID")
    firm_id: UUID = Field(..., description="Firm ID that owns the template")
    name: str = Field(..., description="Template name")
    letterhead_text: Optional[str] = Field(default=None, description="Letterhead text")
    opening_paragraph: Optional[str] = Field(default=None, description="Opening paragraph text")
    closing_paragraph: Optional[str] = Field(default=None, description="Closing paragraph text")
    sections: Optional[List[str]] = Field(default=None, description="List of section names")
    is_default: bool = Field(..., description="Whether this is the default template for the firm")
    created_by: Optional[UUID] = Field(default=None, description="User ID who created the template")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "firm_id": "123e4567-e89b-12d3-a456-426614174001",
                "name": "Standard Demand Letter",
                "letterhead_text": "Law Firm Name\nAddress\nPhone",
                "opening_paragraph": "Dear Sir/Madam,",
                "closing_paragraph": "Sincerely,\nAttorney Name",
                "sections": ["Introduction", "Facts", "Legal Basis", "Demand"],
                "is_default": True,
                "created_by": None,
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z",
            }
        }


class TemplateListResponse(PaginatedResponse[TemplateResponse]):
    """Schema for paginated template list response."""
    pass

