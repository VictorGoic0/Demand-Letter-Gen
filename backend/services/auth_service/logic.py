"""
Business logic for authentication service.
"""
import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from uuid import UUID

from shared.models.user import User
from shared.models.firm import Firm
from shared.exceptions import NotFoundException
from .schemas import LoginResponse

logger = logging.getLogger(__name__)


def login_user(email: str, password: str, db: Session) -> LoginResponse:
    """
    Authenticate a user by email (mock auth - password not validated).
    
    Args:
        email: User email address
        password: User password (not validated in mock auth)
        db: Database session
        
    Returns:
        LoginResponse with user and firm information
        
    Raises:
        NotFoundException: If user with email doesn't exist
    """
    try:
        # Query user by email
        user = db.query(User).filter(User.email == email).one()
        
        # Get firm information
        firm = db.query(Firm).filter(Firm.id == user.firm_id).one()
        
        # Return login response
        return LoginResponse(
            email=user.email,
            userId=str(user.id),
            firmId=str(user.firm_id),
            firmName=firm.name,
            role=user.role,
        )
    except NoResultFound:
        logger.warning(f"Login attempt with non-existent email: {email}")
        raise NotFoundException(f"User with email {email} not found")
    except Exception as e:
        logger.error(f"Error during login for email {email}: {str(e)}")
        raise

