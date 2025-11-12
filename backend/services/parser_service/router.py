"""
FastAPI router for parser service endpoints.
"""
import logging
from uuid import UUID
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from shared.database import get_db
from .schemas import (
    ParseRequest,
    ParseResponse,
    ParseBatchResponse,
)
from .logic import (
    parse_document,
    parse_documents_batch,
)

logger = logging.getLogger(__name__)

# Create router with prefix "/parse"
router = APIRouter(prefix="/parse", tags=["parser"])


@router.post(
    "/document/{document_id}",
    response_model=ParseResponse,
    status_code=status.HTTP_200_OK,
    summary="Parse a single document",
    description="Parse a PDF document by ID, extracting text and metadata. Verifies document belongs to firm.",
)
async def parse_document_endpoint(
    document_id: UUID,
    firm_id: UUID = Query(..., description="Firm ID (query parameter for MVP)"),
    db: Session = Depends(get_db),
):
    """
    Parse a single document.
    
    - **document_id**: Document ID (path parameter)
    - **firm_id**: Firm ID (query parameter)
    
    Returns parsed text and metadata.
    """
    try:
        result = parse_document(
            db=db,
            document_id=document_id,
            firm_id=firm_id,
        )
        return result
        
    except Exception as e:
        logger.error(f"Error in parse document endpoint: {str(e)}")
        raise


@router.post(
    "/batch",
    response_model=ParseBatchResponse,
    status_code=status.HTTP_200_OK,
    summary="Parse multiple documents",
    description="Parse multiple PDF documents in batch. Verifies all documents belong to firm. Maximum 10 documents per request.",
)
async def parse_batch_endpoint(
    request: ParseRequest,
    firm_id: UUID = Query(..., description="Firm ID (query parameter for MVP)"),
    db: Session = Depends(get_db),
):
    """
    Parse multiple documents in batch.
    
    - **document_ids**: List of document IDs to parse (max 10)
    - **firm_id**: Firm ID (query parameter)
    
    Returns batch results with success/failure status for each document.
    """
    try:
        # Validate document count
        if len(request.document_ids) == 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="At least one document ID is required",
            )
        
        if len(request.document_ids) > 10:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Maximum 10 documents allowed per batch request",
            )
        
        # Parse documents
        results = parse_documents_batch(
            db=db,
            document_ids=request.document_ids,
            firm_id=firm_id,
        )
        
        # Calculate statistics
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        
        return ParseBatchResponse(
            results=results,
            total=len(results),
            successful=successful,
            failed=failed,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in parse batch endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to parse documents",
        )

