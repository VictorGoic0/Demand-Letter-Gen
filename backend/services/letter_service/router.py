"""
FastAPI router for letter service endpoints.
"""
import logging
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from shared.database import get_db
from shared.schemas import PaginatedResponse
from shared.exceptions import register_exception_handlers
from .schemas import (
    LetterResponse,
    LetterListResponse,
    LetterUpdate,
)
from .logic import (
    get_letters,
    get_letter_by_id,
    update_letter,
    delete_letter,
)

logger = logging.getLogger(__name__)

# Create router with firm_id in path
router = APIRouter(prefix="/{firm_id}/letters", tags=["letters"])


@router.get(
    "/",
    response_model=LetterListResponse,
    status_code=status.HTTP_200_OK,
    summary="List letters",
    description="Get a paginated list of letters for a firm with optional sorting.",
)
async def list_letters_endpoint(
    firm_id: UUID,
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Number of items per page"),
    sort_by: Optional[str] = Query(None, description="Field to sort by (created_at, updated_at, title, status)"),
    sort_order: str = Query("desc", description="Sort order (asc, desc)"),
    db: Session = Depends(get_db),
):
    """
    List letters for a firm.
    
    - **firm_id**: Firm ID (path parameter)
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20, max: 100)
    - **sort_by**: Field to sort by (created_at, updated_at, title, status)
    - **sort_order**: Sort order (asc, desc)
    
    Returns paginated list of letters.
    """
    try:
        logger.info(f"GET /{firm_id}/letters/ - Request received: page={page}, page_size={page_size}, sort_by={sort_by}, sort_order={sort_order}")
        
        # Validate sort_by
        if sort_by and sort_by not in ["created_at", "updated_at", "title", "status"]:
            logger.warning(f"Invalid sort_by value: {sort_by}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="sort_by must be one of: created_at, updated_at, title, status",
            )
        
        # Validate sort_order
        if sort_order not in ["asc", "desc"]:
            logger.warning(f"Invalid sort_order value: {sort_order}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="sort_order must be 'asc' or 'desc'",
            )
        
        # Get letters
        logger.info(f"Calling get_letters logic for firm {firm_id}")
        letters, total = get_letters(
            db=db,
            firm_id=firm_id,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        
        logger.info(f"Successfully retrieved {len(letters)} letters (total: {total}) for firm {firm_id}")
        
        # Create paginated response
        response = LetterListResponse.create(
            items=letters,
            total=total,
            page=page,
            page_size=page_size,
        )
        
        logger.info(f"Returning paginated response: page={page}, page_size={page_size}, total={total}, items_count={len(letters)}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in list endpoint for firm {firm_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve letters",
        )


@router.get(
    "/{letter_id}",
    response_model=LetterResponse,
    status_code=status.HTTP_200_OK,
    summary="Get letter by ID",
    description="Get letter data by ID, verifying it belongs to the firm.",
)
async def get_letter_endpoint(
    firm_id: UUID,
    letter_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get a letter by ID.
    
    - **firm_id**: Firm ID (path parameter)
    - **letter_id**: Letter ID (path parameter)
    
    Returns letter data with presigned URL if .docx exists.
    """
    try:
        letter = get_letter_by_id(
            db=db,
            letter_id=letter_id,
            firm_id=firm_id,
        )
        return letter
        
    except Exception as e:
        logger.error(f"Error in get endpoint: {str(e)}")
        raise


@router.put(
    "/{letter_id}",
    response_model=LetterResponse,
    status_code=status.HTTP_200_OK,
    summary="Update letter",
    description="Update a letter's title and/or content, verifying it belongs to the firm.",
)
async def update_letter_endpoint(
    firm_id: UUID,
    letter_id: UUID,
    letter_update: LetterUpdate,
    db: Session = Depends(get_db),
):
    """
    Update a letter.
    
    - **firm_id**: Firm ID (path parameter)
    - **letter_id**: Letter ID (path parameter)
    - **letter_update**: Letter update data (title and/or content)
    
    Returns updated letter data.
    """
    try:
        letter = update_letter(
            db=db,
            letter_id=letter_id,
            firm_id=firm_id,
            title=letter_update.title,
            content=letter_update.content,
        )
        return letter
        
    except Exception as e:
        logger.error(f"Error in update endpoint: {str(e)}")
        raise


@router.delete(
    "/{letter_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete letter",
    description="Delete a letter from S3 and database, verifying it belongs to the firm.",
)
async def delete_letter_endpoint(
    firm_id: UUID,
    letter_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Delete a letter.
    
    - **firm_id**: Firm ID (path parameter)
    - **letter_id**: Letter ID (path parameter)
    
    Returns 204 No Content on success.
    """
    try:
        delete_letter(
            db=db,
            letter_id=letter_id,
            firm_id=firm_id,
        )
        return Response(status_code=status.HTTP_204_NO_CONTENT)
        
    except Exception as e:
        logger.error(f"Error in delete endpoint: {str(e)}")
        raise

