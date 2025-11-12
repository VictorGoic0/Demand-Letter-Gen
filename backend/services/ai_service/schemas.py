"""
Pydantic schemas for AI service API requests and responses.
"""
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, field_validator


class GenerateRequest(BaseModel):
    """Schema for letter generation request."""
    template_id: UUID = Field(..., description="Template ID to use for generation")
    document_ids: List[UUID] = Field(
        ...,
        min_length=1,
        max_length=5,
        description="List of document IDs to use as source material (max 5 documents)"
    )
    title: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Optional title for the generated letter"
    )
    
    @field_validator("document_ids")
    @classmethod
    def validate_document_count(cls, v):
        """Validate document count is within limits."""
        if len(v) == 0:
            raise ValueError("At least one document is required")
        if len(v) > 5:
            raise ValueError("Maximum 5 documents allowed per letter generation")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "template_id": "123e4567-e89b-12d3-a456-426614174000",
                "document_ids": [
                    "123e4567-e89b-12d3-a456-426614174001",
                    "123e4567-e89b-12d3-a456-426614174002"
                ],
                "title": "Demand Letter - Case #2024-001"
            }
        }


class GenerateResponse(BaseModel):
    """Schema for letter generation response."""
    letter_id: UUID = Field(..., description="ID of the generated letter")
    content: str = Field(..., description="HTML content of the generated letter")
    status: str = Field(
        default="draft",
        description="Status of the letter (always 'draft' for newly generated letters)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "letter_id": "123e4567-e89b-12d3-a456-426614174000",
                "content": "<h1>Demand Letter</h1><p>Letter content...</p>",
                "status": "draft"
            }
        }

