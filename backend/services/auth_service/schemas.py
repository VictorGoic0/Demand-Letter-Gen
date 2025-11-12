"""
Schemas for authentication endpoints.
"""
from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Request schema for login endpoint."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password (not validated in mock auth)")


class LoginResponse(BaseModel):
    """Response schema for login endpoint."""
    email: str = Field(..., description="User email address")
    userId: str = Field(..., description="User ID (UUID as string)")
    firmId: str = Field(..., description="Firm ID (UUID as string)")
    firmName: str = Field(..., description="Firm name")

