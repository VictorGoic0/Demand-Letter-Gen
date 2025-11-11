"""
Pydantic schemas for document service API requests and responses.
"""
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, field_validator, HttpUrl
from shared.schemas import PaginatedResponse


class DocumentBase(BaseModel):
    """Base schema for document data."""
    filename: str = Field(..., description="Original filename")
    file_size: int = Field(..., ge=1, description="File size in bytes")
    mime_type: str = Field(..., description="MIME type of the file")


class DocumentCreate(BaseModel):
    """Schema for document creation (internal use)."""
    firm_id: UUID = Field(..., description="Firm ID that owns the document")
    uploaded_by: Optional[UUID] = Field(default=None, description="User ID who uploaded the document")
    filename: str = Field(..., description="Original filename")
    file_size: int = Field(..., ge=1, description="File size in bytes")
    s3_key: str = Field(..., description="S3 object key")
    mime_type: str = Field(..., description="MIME type of the file")
    
    @field_validator("filename")
    @classmethod
    def validate_filename(cls, v):
        """Validate filename is not empty."""
        if not v or not v.strip():
            raise ValueError("Filename cannot be empty")
        return v.strip()
    
    @field_validator("mime_type")
    @classmethod
    def validate_mime_type(cls, v):
        """Validate MIME type is allowed."""
        allowed_types = ["application/pdf"]
        if v not in allowed_types:
            raise ValueError(f"MIME type must be one of: {', '.join(allowed_types)}")
        return v
    
    @field_validator("file_size")
    @classmethod
    def validate_file_size(cls, v):
        """Validate file size is within limits (50MB max)."""
        max_size = 50 * 1024 * 1024  # 50MB in bytes
        if v > max_size:
            raise ValueError(f"File size cannot exceed {max_size / (1024 * 1024):.0f}MB")
        return v


class DocumentResponse(BaseModel):
    """Schema for document response."""
    id: UUID = Field(..., description="Document ID")
    firm_id: UUID = Field(..., description="Firm ID that owns the document")
    uploaded_by: Optional[UUID] = Field(default=None, description="User ID who uploaded the document")
    filename: str = Field(..., description="Original filename")
    file_size: int = Field(..., description="File size in bytes")
    mime_type: str = Field(..., description="MIME type of the file")
    uploaded_at: datetime = Field(..., description="Upload timestamp")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "firm_id": "123e4567-e89b-12d3-a456-426614174001",
                "uploaded_by": None,
                "filename": "medical_records.pdf",
                "file_size": 1048576,
                "mime_type": "application/pdf",
                "uploaded_at": "2024-01-15T10:30:00Z",
            }
        }


class DocumentListResponse(PaginatedResponse[DocumentResponse]):
    """Schema for paginated document list response."""
    pass


class UploadResponse(BaseModel):
    """Schema for document upload response."""
    success: bool = Field(default=True, description="Indicates if upload was successful")
    message: str = Field(default="Document uploaded successfully", description="Success message")
    document: DocumentResponse = Field(..., description="Uploaded document metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Document uploaded successfully",
                "document": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "firm_id": "123e4567-e89b-12d3-a456-426614174001",
                    "uploaded_by": None,
                    "filename": "medical_records.pdf",
                    "file_size": 1048576,
                    "mime_type": "application/pdf",
                    "uploaded_at": "2024-01-15T10:30:00Z",
                }
            }
        }


class DownloadUrlResponse(BaseModel):
    """Schema for presigned download URL response."""
    url: HttpUrl = Field(..., description="Presigned download URL")
    expires_in: int = Field(..., description="URL expiration time in seconds")
    document_id: UUID = Field(..., description="Document ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://s3.amazonaws.com/bucket/key?signature=...",
                "expires_in": 3600,
                "document_id": "123e4567-e89b-12d3-a456-426614174000",
            }
        }

