"""
Common Pydantic schemas for API responses and pagination.
"""
from typing import Optional, List, Generic, TypeVar, Any
from pydantic import BaseModel, Field, field_validator

T = TypeVar("T")


class SuccessResponse(BaseModel):
    """Standard success response schema."""
    success: bool = Field(default=True, description="Indicates if the operation was successful")
    message: Optional[str] = Field(default=None, description="Optional success message")
    data: Optional[Any] = Field(default=None, description="Optional response data")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Operation completed successfully",
                "data": None,
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response schema."""
    success: bool = Field(default=False, description="Indicates if the operation failed")
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(default=None, description="Optional detailed error information")
    code: Optional[str] = Field(default=None, description="Optional error code")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "Resource not found",
                "detail": "The requested resource does not exist",
                "code": "NOT_FOUND",
            }
        }


class PaginationParams(BaseModel):
    """Pagination parameters for list endpoints."""
    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(default=20, ge=1, le=100, description="Number of items per page")
    sort_by: Optional[str] = Field(default=None, description="Field to sort by")
    sort_order: Optional[str] = Field(default="asc", description="Sort order: 'asc' or 'desc'")
    
    @field_validator("sort_order")
    @classmethod
    def validate_sort_order(cls, v):
        """Validate sort order is 'asc' or 'desc'."""
        if v and v.lower() not in ["asc", "desc"]:
            raise ValueError("sort_order must be 'asc' or 'desc'")
        return v.lower() if v else "asc"
    
    @property
    def offset(self) -> int:
        """Calculate offset for database queries."""
        return (self.page - 1) * self.page_size
    
    @property
    def limit(self) -> int:
        """Get limit for database queries."""
        return self.page_size
    
    class Config:
        json_schema_extra = {
            "example": {
                "page": 1,
                "page_size": 20,
                "sort_by": "created_at",
                "sort_order": "desc",
            }
        }


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response schema."""
    items: List[T] = Field(..., description="List of items in the current page")
    total: int = Field(..., ge=0, description="Total number of items")
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, description="Number of items per page")
    total_pages: int = Field(..., ge=0, description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_previous: bool = Field(..., description="Whether there is a previous page")
    
    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        page: int,
        page_size: int,
    ) -> "PaginatedResponse[T]":
        """
        Create a paginated response from items and pagination parameters.
        
        Args:
            items: List of items for the current page
            total: Total number of items
            page: Current page number
            page_size: Number of items per page
            
        Returns:
            PaginatedResponse instance
        """
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1,
        )
    
    class Config:
        json_schema_extra = {
            "example": {
                "items": [],
                "total": 0,
                "page": 1,
                "page_size": 20,
                "total_pages": 0,
                "has_next": False,
                "has_previous": False,
            }
        }

