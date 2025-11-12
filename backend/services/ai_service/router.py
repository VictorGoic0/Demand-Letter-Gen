"""
FastAPI router for AI service endpoints.
"""
import logging
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from shared.database import get_db
from shared.exceptions import (
    ValidationException,
    TemplateNotFoundException,
    DocumentNotFoundException,
    ForbiddenException,
    OpenAIException,
    ParserException,
)
from .schemas import GenerateRequest, GenerateResponse
from .logic import generate_letter

logger = logging.getLogger(__name__)

# Create router with prefix for generation endpoint
router = APIRouter(prefix="/generate", tags=["ai"])


@router.post(
    "/letter",
    response_model=GenerateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate a demand letter",
    description="Generate a demand letter using AI from a template and source documents. Maximum 5 documents allowed.",
)
async def generate_letter_endpoint(
    firm_id: UUID = Query(..., description="Firm ID (query parameter for MVP)"),
    created_by: Optional[UUID] = Query(None, description="User ID who is creating the letter (optional)"),
    request: GenerateRequest = ...,
    db: Session = Depends(get_db),
):
    """
    Generate a demand letter using AI.
    
    - **firm_id**: Firm ID (query parameter)
    - **created_by**: Optional user ID (query parameter)
    - **template_id**: Template ID to use for generation
    - **document_ids**: List of document IDs (1-5 documents)
    - **title**: Optional title for the letter
    
    Returns the generated letter with ID, content, and status.
    """
    try:
        result = generate_letter(
            db=db,
            firm_id=firm_id,
            created_by=created_by,
            request=request,
        )
        return result
        
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.detail or e.message,
        )
    except (TemplateNotFoundException, DocumentNotFoundException) as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.detail or e.message,
        )
    except ForbiddenException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.detail or e.message,
        )
    except (OpenAIException, ParserException) as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.detail or e.message,
        )
    except Exception as e:
        logger.error(f"Unexpected error generating letter: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while generating the letter",
        )

