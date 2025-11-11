"""
Business logic for document service operations.
"""
import logging
from typing import Optional, List, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc

from shared.models.document import Document
from shared.exceptions import (
    DocumentNotFoundException,
    S3UploadException,
    S3DownloadException,
    ForbiddenException,
)
from shared.s3_client import get_s3_client
from shared.config import get_settings
from shared.utils import sanitize_filename, generate_uuid
from .schemas import DocumentResponse

logger = logging.getLogger(__name__)


def upload_document(
    db: Session,
    firm_id: UUID,
    uploaded_by: Optional[UUID],
    filename: str,
    file_size: int,
    mime_type: str,
    file_content: bytes,
) -> DocumentResponse:
    """
    Upload a document to S3 and create database record.
    
    Args:
        db: Database session
        firm_id: Firm ID that owns the document
        uploaded_by: Optional user ID who uploaded the document
        filename: Original filename
        file_size: File size in bytes
        mime_type: MIME type of the file
        file_content: File content as bytes
        
    Returns:
        DocumentResponse with document metadata
        
    Raises:
        S3UploadException: If S3 upload fails
        ValidationException: If file validation fails
    """
    try:
        settings = get_settings()
        s3_client = get_s3_client()
        
        # Generate unique document ID
        document_id = UUID(generate_uuid())
        
        # Sanitize filename
        sanitized_filename = sanitize_filename(filename)
        
        # Generate unique S3 key: {firm_id}/{document_id}/{sanitized_filename}
        s3_key = f"{firm_id}/{document_id}/{sanitized_filename}"
        
        # Upload to S3
        import io
        file_obj = io.BytesIO(file_content)
        
        try:
            s3_client.upload_fileobj(
                file_obj=file_obj,
                bucket_name=settings.aws.s3_bucket_documents,
                s3_key=s3_key,
                content_type=mime_type,
                metadata={
                    "firm_id": str(firm_id),
                    "document_id": str(document_id),
                    "original_filename": filename,
                },
            )
            logger.info(f"File uploaded to S3: {s3_key}")
        except Exception as e:
            logger.error(f"Failed to upload file to S3: {str(e)}")
            raise S3UploadException(
                message="Failed to upload file to S3",
                detail=str(e),
            )
        
        # Create database record
        document = Document(
            id=document_id,
            firm_id=firm_id,
            uploaded_by=uploaded_by,
            filename=filename,  # Store original filename
            file_size=file_size,
            s3_key=s3_key,
            mime_type=mime_type,
        )
        
        db.add(document)
        db.commit()
        db.refresh(document)
        
        logger.info(f"Document created in database: {document_id}")
        
        return DocumentResponse.model_validate(document)
        
    except S3UploadException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error uploading document: {str(e)}")
        raise


def get_documents(
    db: Session,
    firm_id: UUID,
    page: int = 1,
    page_size: int = 20,
    sort_by: Optional[str] = None,
    sort_order: str = "desc",
) -> Tuple[List[DocumentResponse], int]:
    """
    Get paginated list of documents for a firm.
    
    Args:
        db: Database session
        firm_id: Firm ID to filter documents
        page: Page number (1-indexed)
        page_size: Number of items per page
        sort_by: Field to sort by (filename, uploaded_at)
        sort_order: Sort order (asc, desc)
        
    Returns:
        Tuple of (list of DocumentResponse, total count)
    """
    try:
        # Base query filtered by firm_id
        query = db.query(Document).filter(Document.firm_id == firm_id)
        
        # Apply sorting
        if sort_by == "filename":
            order_func = asc(Document.filename) if sort_order == "asc" else desc(Document.filename)
        elif sort_by == "uploaded_at" or sort_by is None:
            order_func = asc(Document.uploaded_at) if sort_order == "asc" else desc(Document.uploaded_at)
        else:
            # Default to uploaded_at desc
            order_func = desc(Document.uploaded_at)
        
        query = query.order_by(order_func)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * page_size
        documents = query.offset(offset).limit(page_size).all()
        
        # Convert to response models
        document_responses = [DocumentResponse.model_validate(doc) for doc in documents]
        
        logger.info(f"Retrieved {len(document_responses)} documents for firm {firm_id}")
        
        return document_responses, total
        
    except Exception as e:
        logger.error(f"Error getting documents: {str(e)}")
        raise


def get_document_by_id(
    db: Session,
    document_id: UUID,
    firm_id: UUID,
) -> DocumentResponse:
    """
    Get a document by ID, verifying it belongs to the firm.
    
    Args:
        db: Database session
        document_id: Document ID
        firm_id: Firm ID to verify ownership
        
    Returns:
        DocumentResponse with document metadata
        
    Raises:
        DocumentNotFoundException: If document not found
        ForbiddenException: If document doesn't belong to firm
    """
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        
        if not document:
            raise DocumentNotFoundException(document_id=str(document_id))
        
        # Verify firm-level isolation
        if document.firm_id != firm_id:
            raise ForbiddenException(
                message="Access denied",
                detail="Document does not belong to this firm",
            )
        
        return DocumentResponse.model_validate(document)
        
    except (DocumentNotFoundException, ForbiddenException):
        raise
    except Exception as e:
        logger.error(f"Error getting document: {str(e)}")
        raise


def delete_document(
    db: Session,
    document_id: UUID,
    firm_id: UUID,
) -> None:
    """
    Delete a document from S3 and database.
    
    Args:
        db: Database session
        document_id: Document ID
        firm_id: Firm ID to verify ownership
        
    Returns:
        None
        
    Raises:
        DocumentNotFoundException: If document not found
        ForbiddenException: If document doesn't belong to firm
        S3UploadException: If S3 deletion fails
    """
    try:
        settings = get_settings()
        s3_client = get_s3_client()
        
        # Get document and verify ownership
        document = db.query(Document).filter(Document.id == document_id).first()
        
        if not document:
            raise DocumentNotFoundException(document_id=str(document_id))
        
        # Verify firm-level isolation
        if document.firm_id != firm_id:
            raise ForbiddenException(
                message="Access denied",
                detail="Document does not belong to this firm",
            )
        
        # Delete from S3
        try:
            s3_client.delete_file(
                bucket_name=settings.aws.s3_bucket_documents,
                s3_key=document.s3_key,
            )
            logger.info(f"File deleted from S3: {document.s3_key}")
        except Exception as e:
            logger.error(f"Failed to delete file from S3: {str(e)}")
            raise S3UploadException(
                message="Failed to delete file from S3",
                detail=str(e),
            )
        
        # Delete from database
        db.delete(document)
        db.commit()
        
        logger.info(f"Document deleted: {document_id}")
        
    except (DocumentNotFoundException, ForbiddenException, S3UploadException):
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting document: {str(e)}")
        raise


def generate_download_url(
    db: Session,
    document_id: UUID,
    firm_id: UUID,
    expiration: int = 3600,
) -> str:
    """
    Generate a presigned download URL for a document.
    
    Args:
        db: Database session
        document_id: Document ID
        firm_id: Firm ID to verify ownership
        expiration: URL expiration time in seconds (default: 1 hour)
        
    Returns:
        Presigned URL string
        
    Raises:
        DocumentNotFoundException: If document not found
        ForbiddenException: If document doesn't belong to firm
        S3DownloadException: If URL generation fails
    """
    try:
        settings = get_settings()
        s3_client = get_s3_client()
        
        # Get document and verify ownership
        document = db.query(Document).filter(Document.id == document_id).first()
        
        if not document:
            raise DocumentNotFoundException(document_id=str(document_id))
        
        # Verify firm-level isolation
        if document.firm_id != firm_id:
            raise ForbiddenException(
                message="Access denied",
                detail="Document does not belong to this firm",
            )
        
        # Generate presigned URL
        try:
            url = s3_client.generate_presigned_url(
                bucket_name=settings.aws.s3_bucket_documents,
                s3_key=document.s3_key,
                expiration=expiration,
                http_method="GET",
            )
            logger.info(f"Presigned URL generated for document: {document_id}")
            return url
        except Exception as e:
            logger.error(f"Failed to generate presigned URL: {str(e)}")
            raise S3DownloadException(
                message="Failed to generate download URL",
                detail=str(e),
            )
        
    except (DocumentNotFoundException, ForbiddenException, S3DownloadException):
        raise
    except Exception as e:
        logger.error(f"Error generating download URL: {str(e)}")
        raise

