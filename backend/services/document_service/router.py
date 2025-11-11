"""
FastAPI router for document service endpoints.
"""
import logging
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, UploadFile, File, Query, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from shared.database import get_db
from shared.schemas import PaginationParams, PaginatedResponse
from shared.exceptions import register_exception_handlers
from .schemas import (
    DocumentResponse,
    DocumentListResponse,
    UploadResponse,
    DownloadUrlResponse,
)
from .logic import (
    upload_document,
    get_documents,
    get_document_by_id,
    delete_document,
    generate_download_url,
)

logger = logging.getLogger(__name__)

# Create router with firm_id in path
router = APIRouter(prefix="/{firm_id}/documents", tags=["documents"])


@router.post(
    "/",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a document",
    description="Upload a PDF document to S3 and create a database record. Maximum file size is 50MB.",
)
async def upload_document_endpoint(
    firm_id: UUID,
    file: UploadFile = File(..., description="PDF file to upload"),
    uploaded_by: Optional[UUID] = Query(None, description="User ID who uploaded the document (optional)"),
    db: Session = Depends(get_db),
):
    """
    Upload a document.
    
    - **firm_id**: Firm ID (path parameter)
    - **file**: PDF file to upload (multipart/form-data)
    - **uploaded_by**: Optional user ID (query parameter)
    
    Returns document metadata on success.
    """
    try:
        # Validate file type
        if file.content_type != "application/pdf":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Only PDF files are allowed",
            )
        
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)
        
        # Validate file size (50MB max)
        max_size = 50 * 1024 * 1024
        if file_size > max_size:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"File size cannot exceed {max_size / (1024 * 1024):.0f}MB",
            )
        
        # Upload document
        document = upload_document(
            db=db,
            firm_id=firm_id,
            uploaded_by=uploaded_by,
            filename=file.filename or "document.pdf",
            file_size=file_size,
            mime_type=file.content_type or "application/pdf",
            file_content=file_content,
        )
        
        return UploadResponse(
            success=True,
            message="Document uploaded successfully",
            document=document,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in upload endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload document",
        )


@router.get(
    "/",
    response_model=DocumentListResponse,
    status_code=status.HTTP_200_OK,
    summary="List documents",
    description="Get a paginated list of documents for a firm with optional sorting.",
)
async def list_documents_endpoint(
    firm_id: UUID,
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Number of items per page"),
    sort_by: Optional[str] = Query(None, description="Field to sort by (filename, uploaded_at)"),
    sort_order: str = Query("desc", description="Sort order (asc, desc)"),
    db: Session = Depends(get_db),
):
    """
    List documents for a firm.
    
    - **firm_id**: Firm ID (path parameter)
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20, max: 100)
    - **sort_by**: Field to sort by (filename, uploaded_at)
    - **sort_order**: Sort order (asc, desc)
    
    Returns paginated list of documents.
    """
    try:
        # Validate sort_by
        if sort_by and sort_by not in ["filename", "uploaded_at"]:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="sort_by must be 'filename' or 'uploaded_at'",
            )
        
        # Validate sort_order
        if sort_order not in ["asc", "desc"]:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="sort_order must be 'asc' or 'desc'",
            )
        
        # Get documents
        documents, total = get_documents(
            db=db,
            firm_id=firm_id,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        
        # Create paginated response
        return DocumentListResponse.create(
            items=documents,
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
            detail="Failed to retrieve documents",
        )


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
    status_code=status.HTTP_200_OK,
    summary="Get document by ID",
    description="Get document metadata by ID, verifying it belongs to the firm.",
)
async def get_document_endpoint(
    firm_id: UUID,
    document_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get a document by ID.
    
    - **firm_id**: Firm ID (path parameter)
    - **document_id**: Document ID (path parameter)
    
    Returns document metadata.
    """
    try:
        document = get_document_by_id(
            db=db,
            document_id=document_id,
            firm_id=firm_id,
        )
        return document
        
    except Exception as e:
        logger.error(f"Error in get endpoint: {str(e)}")
        raise


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete document",
    description="Delete a document from S3 and database, verifying it belongs to the firm.",
)
async def delete_document_endpoint(
    firm_id: UUID,
    document_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Delete a document.
    
    - **firm_id**: Firm ID (path parameter)
    - **document_id**: Document ID (path parameter)
    
    Returns 204 No Content on success.
    """
    try:
        delete_document(
            db=db,
            document_id=document_id,
            firm_id=firm_id,
        )
        return Response(status_code=status.HTTP_204_NO_CONTENT)
        
    except Exception as e:
        logger.error(f"Error in delete endpoint: {str(e)}")
        raise


@router.get(
    "/{document_id}/download",
    response_model=DownloadUrlResponse,
    status_code=status.HTTP_200_OK,
    summary="Get download URL",
    description="Generate a presigned download URL for a document (valid for 1 hour).",
)
async def download_document_endpoint(
    firm_id: UUID,
    document_id: UUID,
    expiration: int = Query(3600, ge=60, le=86400, description="URL expiration in seconds (default: 3600, max: 86400)"),
    db: Session = Depends(get_db),
):
    """
    Get a presigned download URL for a document.
    
    - **firm_id**: Firm ID (path parameter)
    - **document_id**: Document ID (path parameter)
    - **expiration**: URL expiration time in seconds (default: 3600, max: 86400)
    
    Returns presigned URL with expiration time.
    """
    try:
        url = generate_download_url(
            db=db,
            document_id=document_id,
            firm_id=firm_id,
            expiration=expiration,
        )
        
        return DownloadUrlResponse(
            url=url,
            expires_in=expiration,
            document_id=document_id,
        )
        
    except Exception as e:
        logger.error(f"Error in download endpoint: {str(e)}")
        raise

