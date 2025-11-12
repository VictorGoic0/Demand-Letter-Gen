"""
FastAPI router for authentication endpoints.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from shared.database import get_db
from shared.exceptions import NotFoundException
from .schemas import LoginRequest, LoginResponse
from .logic import login_user

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="", tags=["auth"])


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Login user",
    description="Authenticate a user by email (mock auth - password not validated). Returns user and firm information.",
)
async def login_endpoint(
    login_request: LoginRequest,
    db: Session = Depends(get_db),
):
    """
    Login endpoint.
    
    - **email**: User email address
    - **password**: User password (not validated in mock auth)
    
    Returns user and firm information if user exists.
    """
    try:
        result = login_user(login_request.email, login_request.password, db)
        return result
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during login",
        )

