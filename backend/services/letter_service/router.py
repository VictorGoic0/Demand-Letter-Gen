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
    FinalizeResponse,
    ExportResponse,
)
from .logic import (
    get_letters,
    get_letter_by_id,
    update_letter,
    delete_letter,
    finalize_letter,
    export_letter,
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
        # Validate sort_by
        if sort_by and sort_by not in ["created_at", "updated_at", "title", "status"]:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="sort_by must be one of: created_at, updated_at, title, status",
            )
        
        # Validate sort_order
        if sort_order not in ["asc", "desc"]:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="sort_order must be 'asc' or 'desc'",
            )
        
        # Get letters
        letters, total = get_letters(
            db=db,
            firm_id=firm_id,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        
        # Create paginated response
        return LetterListResponse.create(
            items=letters,
            total=total,
            page=page,
            page_size=page_size,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in list endpoint: {str(e)}")
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


@router.post(
    "/{letter_id}/finalize",
    response_model=FinalizeResponse,
    status_code=status.HTTP_200_OK,
    summary="Finalize letter",
    description="Finalize a letter by generating DOCX and updating status to 'created'. Works on letters with status 'draft' OR 'created' (allows re-finalizing).",
)
async def finalize_letter_endpoint(
    firm_id: UUID,
    letter_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Finalize a letter.
    
    - **firm_id**: Firm ID (path parameter)
    - **letter_id**: Letter ID (path parameter)
    
    Generates DOCX file, uploads to S3, updates status to 'created', and returns letter with download URL.
    """
    try:
        letter = finalize_letter(
            db=db,
            letter_id=letter_id,
            firm_id=firm_id,
        )
        
        # Build response
        return FinalizeResponse(
            letter=letter,
            download_url=letter.docx_url,
            message="Letter finalized successfully",
        )
        
    except Exception as e:
        logger.error(f"Error in finalize endpoint: {str(e)}")
        raise


@router.post(
    "/{letter_id}/export",
    response_model=ExportResponse,
    status_code=status.HTTP_200_OK,
    summary="Export letter",
    description="Export a letter by returning existing presigned URL or generating new DOCX if none exists.",
)
async def export_letter_endpoint(
    firm_id: UUID,
    letter_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Export a letter.
    
    - **firm_id**: Firm ID (path parameter)
    - **letter_id**: Letter ID (path parameter)
    
    Returns presigned URL for downloading the DOCX file. If no DOCX exists, generates one first.
    """
    try:
        download_url = export_letter(
            db=db,
            letter_id=letter_id,
            firm_id=firm_id,
        )
        
        # Build response
        return ExportResponse(
            download_url=download_url,
            expires_in=3600,  # 1 hour
            letter_id=letter_id,
            message="Letter exported successfully",
        )
        
    except Exception as e:
        logger.error(f"Error in export endpoint: {str(e)}")
        raise

