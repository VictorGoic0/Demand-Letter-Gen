"""
Pydantic schemas for letter service API requests and responses.
"""
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, HttpUrl
from shared.schemas import PaginatedResponse


class LetterBase(BaseModel):
    """Base schema for letter data."""
    title: str = Field(..., description="Letter title")
    content: str = Field(..., description="HTML content of the letter")


class DocumentMetadata(BaseModel):
    """Schema for source document metadata in letter response."""
    id: UUID = Field(..., description="Document ID")
    filename: str = Field(..., description="Document filename")
    file_size: int = Field(..., description="File size in bytes")
    uploaded_at: datetime = Field(..., description="Upload timestamp")
    
    class Config:
        from_attributes = True


class LetterResponse(BaseModel):
    """Schema for letter response."""
    id: UUID = Field(..., description="Letter ID")
    title: str = Field(..., description="Letter title")
    content: str = Field(..., description="HTML content of the letter")
    status: str = Field(..., description="Letter status (draft or created)")
    template_id: Optional[UUID] = Field(default=None, description="Template ID used to generate the letter")
    template_name: Optional[str] = Field(default=None, description="Template name")
    source_documents: List[DocumentMetadata] = Field(default_factory=list, description="List of source document metadata")
    docx_url: Optional[HttpUrl] = Field(default=None, description="Presigned URL for downloading the .docx file")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Demand Letter - John Doe",
                "content": "<html><body><p>Dear Sir/Madam,</p>...</body></html>",
                "status": "draft",
                "template_id": "123e4567-e89b-12d3-a456-426614174001",
                "template_name": "Standard Demand Letter Template",
                "source_documents": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174002",
                        "filename": "medical_records.pdf",
                        "file_size": 1048576,
                        "uploaded_at": "2024-01-15T10:30:00Z"
                    }
                ],
                "docx_url": None,
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z",
            }
        }


class LetterListResponse(PaginatedResponse[LetterResponse]):
    """Schema for paginated letter list response."""
    pass


class LetterUpdate(BaseModel):
    """Schema for updating a letter."""
    title: Optional[str] = Field(default=None, description="Letter title")
    content: Optional[str] = Field(default=None, description="HTML content of the letter")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Updated Demand Letter - John Doe",
                "content": "<html><body><p>Updated content...</p></body></html>",
            }
        }


class FinalizeResponse(BaseModel):
    """Schema for letter finalization response."""
    letter: LetterResponse = Field(..., description="Updated letter with finalized status")
    download_url: HttpUrl = Field(..., description="Presigned URL for downloading the .docx file")
    message: str = Field(default="Letter finalized successfully", description="Success message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "letter": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "title": "Demand Letter - John Doe",
                    "content": "<html><body><p>...</p></body></html>",
                    "status": "created",
                    "template_id": "123e4567-e89b-12d3-a456-426614174001",
                    "template_name": "Standard Demand Letter Template",
                    "source_documents": [],
                    "docx_url": "https://s3.amazonaws.com/bucket/key?signature=...",
                    "created_at": "2024-01-15T10:30:00Z",
                    "updated_at": "2024-01-15T10:30:00Z",
                },
                "download_url": "https://s3.amazonaws.com/bucket/key?signature=...",
                "message": "Letter finalized successfully",
            }
        }


class ExportResponse(BaseModel):
    """Schema for letter export response."""
    download_url: HttpUrl = Field(..., description="Presigned URL for downloading the .docx file")
    expires_in: int = Field(..., description="URL expiration time in seconds")
    letter_id: UUID = Field(..., description="Letter ID")
    message: str = Field(default="Letter exported successfully", description="Success message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "download_url": "https://s3.amazonaws.com/bucket/key?signature=...",
                "expires_in": 3600,
                "letter_id": "123e4567-e89b-12d3-a456-426614174000",
                "message": "Letter exported successfully",
            }
        }

