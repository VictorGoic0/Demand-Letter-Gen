"""
Pydantic schemas for parser service API requests and responses.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field


class ParseRequest(BaseModel):
    """Schema for parse request with document IDs."""
    document_ids: List[UUID] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="List of document IDs to parse (max 10 documents)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "document_ids": [
                    "123e4567-e89b-12d3-a456-426614174000",
                    "123e4567-e89b-12d3-a456-426614174001"
                ]
            }
        }


class ParseResponse(BaseModel):
    """Schema for parse response with extracted text and metadata."""
    document_id: UUID = Field(..., description="Document ID")
    extracted_text: str = Field(..., description="Extracted text from PDF")
    page_count: int = Field(..., ge=0, description="Number of pages in PDF")
    file_size: int = Field(..., ge=0, description="File size in bytes")
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional PDF metadata (title, author, creation date, etc.)"
    )
    success: bool = Field(default=True, description="Whether parsing was successful")
    error: Optional[str] = Field(default=None, description="Error message if parsing failed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "123e4567-e89b-12d3-a456-426614174000",
                "extracted_text": "This is the extracted text from the PDF...",
                "page_count": 5,
                "file_size": 1048576,
                "metadata": {
                    "title": "Medical Records",
                    "author": "Dr. Smith",
                    "creation_date": "2024-01-15T10:30:00"
                },
                "success": True,
                "error": None
            }
        }


class ParseBatchResponse(BaseModel):
    """Schema for batch parse response."""
    results: List[ParseResponse] = Field(..., description="List of parse results")
    total: int = Field(..., ge=0, description="Total number of documents processed")
    successful: int = Field(..., ge=0, description="Number of successfully parsed documents")
    failed: int = Field(..., ge=0, description="Number of failed parses")
    
    class Config:
        json_schema_extra = {
            "example": {
                "results": [
                    {
                        "document_id": "123e4567-e89b-12d3-a456-426614174000",
                        "extracted_text": "Extracted text...",
                        "page_count": 5,
                        "file_size": 1048576,
                        "metadata": {},
                        "success": True,
                        "error": None
                    }
                ],
                "total": 1,
                "successful": 1,
                "failed": 0
            }
        }

