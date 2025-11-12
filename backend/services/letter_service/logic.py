"""
Business logic for letter service operations.
"""
import logging
from typing import Optional, List, Tuple
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, asc

from shared.models.letter import GeneratedLetter
from shared.models.letter_document import LetterSourceDocument
from shared.models.template import LetterTemplate
from shared.models.document import Document
from shared.exceptions import (
    LetterNotFoundException,
    S3UploadException,
    ForbiddenException,
)
from shared.s3_client import get_s3_client
from shared.config import get_settings
from .schemas import LetterResponse, DocumentMetadata
from .docx_generator import html_to_docx, generate_filename, save_docx_to_s3

logger = logging.getLogger(__name__)


def get_letters(
    db: Session,
    firm_id: UUID,
    page: int = 1,
    page_size: int = 20,
    sort_by: Optional[str] = None,
    sort_order: str = "desc",
) -> Tuple[List[LetterResponse], int]:
    """
    Get paginated list of letters for a firm.
    
    Args:
        db: Database session
        firm_id: Firm ID to filter letters
        page: Page number (1-indexed)
        page_size: Number of items per page
        sort_by: Field to sort by (created_at, updated_at, title, status)
        sort_order: Sort order (asc, desc)
        
    Returns:
        Tuple of (list of LetterResponse, total count)
    """
    try:
        # Base query filtered by firm_id with eager loading for template only
        # Note: source_documents is a dynamic relationship (lazy="dynamic"), so we can't use joinedload
        query = (
            db.query(GeneratedLetter)
            .filter(GeneratedLetter.firm_id == firm_id)
            .options(
                joinedload(GeneratedLetter.template),
            )
        )
        
        # Apply sorting
        if sort_by == "title":
            order_func = asc(GeneratedLetter.title) if sort_order == "asc" else desc(GeneratedLetter.title)
        elif sort_by == "status":
            order_func = asc(GeneratedLetter.status) if sort_order == "asc" else desc(GeneratedLetter.status)
        elif sort_by == "updated_at":
            order_func = asc(GeneratedLetter.updated_at) if sort_order == "asc" else desc(GeneratedLetter.updated_at)
        elif sort_by == "created_at" or sort_by is None:
            order_func = asc(GeneratedLetter.created_at) if sort_order == "asc" else desc(GeneratedLetter.created_at)
        else:
            # Default to created_at desc
            order_func = desc(GeneratedLetter.created_at)
        
        query = query.order_by(order_func)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * page_size
        letters = query.offset(offset).limit(page_size).all()
        
        # Convert to response models
        settings = get_settings()
        s3_client = get_s3_client()
        letter_responses = []
        for letter in letters:
            # Build source documents metadata
            # source_documents is a dynamic relationship, so we need to call .all() on it
            source_docs = [
                DocumentMetadata(
                    id=doc.id,
                    filename=doc.filename,
                    file_size=doc.file_size,
                    uploaded_at=doc.uploaded_at,
                )
                for doc in letter.source_documents.all()
            ]
            
            # Generate presigned URL if docx exists (for finalized letters)
            docx_url = None
            if letter.docx_s3_key:
                try:
                    docx_url = s3_client.generate_presigned_url(
                        bucket_name=settings.aws.s3_bucket_exports,
                        s3_key=letter.docx_s3_key,
                        expiration=3600,  # 1 hour
                        http_method="GET",
                    )
                except Exception as e:
                    logger.warning(f"Failed to generate presigned URL for letter {letter.id} in list view: {str(e)}")
                    # Don't fail the request if URL generation fails, just leave it as None
            
            # Build response
            letter_response = LetterResponse(
                id=letter.id,
                title=letter.title,
                content=letter.content,
                status=letter.status,
                template_id=letter.template_id,
                template_name=letter.template.name if letter.template else None,
                source_documents=source_docs,
                docx_url=docx_url,
                created_at=letter.created_at,
                updated_at=letter.updated_at,
            )
            letter_responses.append(letter_response)
        
        return letter_responses, total
        
    except Exception as e:
        logger.error(f"Error getting letters for firm {firm_id}: {str(e)}")
        raise


def get_letter_by_id(
    db: Session,
    letter_id: UUID,
    firm_id: UUID,
) -> LetterResponse:
    """
    Get a letter by ID, verifying it belongs to the firm.
    
    Args:
        db: Database session
        letter_id: Letter ID
        firm_id: Firm ID to verify ownership
        
    Returns:
        LetterResponse with full letter data including presigned URL if docx exists
        
    Raises:
        LetterNotFoundException: If letter not found
        ForbiddenException: If letter doesn't belong to firm
    """
    try:
        settings = get_settings()
        s3_client = get_s3_client()
        
        # Get letter with eager loading for template only
        # Note: source_documents is a dynamic relationship (lazy="dynamic"), so we can't use joinedload
        letter = (
            db.query(GeneratedLetter)
            .filter(GeneratedLetter.id == letter_id)
            .options(
                joinedload(GeneratedLetter.template),
            )
            .first()
        )
        
        if not letter:
            raise LetterNotFoundException(letter_id=str(letter_id))
        
        # Verify firm-level isolation
        if letter.firm_id != firm_id:
            raise ForbiddenException(
                message="Access denied",
                detail="Letter does not belong to this firm",
            )
        
        # Build source documents metadata
        # source_documents is a dynamic relationship, so we need to call .all() on it
        source_docs = [
            DocumentMetadata(
                id=doc.id,
                filename=doc.filename,
                file_size=doc.file_size,
                uploaded_at=doc.uploaded_at,
            )
            for doc in letter.source_documents.all()
        ]
        
        # Generate presigned URL if docx exists
        docx_url = None
        if letter.docx_s3_key:
            try:
                docx_url = s3_client.generate_presigned_url(
                    bucket_name=settings.aws.s3_bucket_exports,
                    s3_key=letter.docx_s3_key,
                    expiration=3600,  # 1 hour
                    http_method="GET",
                )
            except Exception as e:
                logger.warning(f"Failed to generate presigned URL for letter {letter_id}: {str(e)}")
                # Don't fail the request if URL generation fails, just leave it as None
        
        # Build response
        letter_response = LetterResponse(
            id=letter.id,
            title=letter.title,
            content=letter.content,
            status=letter.status,
            template_id=letter.template_id,
            template_name=letter.template.name if letter.template else None,
            source_documents=source_docs,
            docx_url=docx_url,
            created_at=letter.created_at,
            updated_at=letter.updated_at,
        )
        
        return letter_response
        
    except (LetterNotFoundException, ForbiddenException):
        raise
    except Exception as e:
        logger.error(f"Error getting letter: {str(e)}")
        raise


def update_letter(
    db: Session,
    letter_id: UUID,
    firm_id: UUID,
    title: Optional[str] = None,
    content: Optional[str] = None,
) -> LetterResponse:
    """
    Update a letter's title and/or content.
    
    Args:
        db: Database session
        letter_id: Letter ID
        firm_id: Firm ID to verify ownership
        title: Optional new title
        content: Optional new content
        
    Returns:
        LetterResponse with updated letter data
        
    Raises:
        LetterNotFoundException: If letter not found
        ForbiddenException: If letter doesn't belong to firm
        ValidationException: If both title and content are None
    """
    try:
        # Get letter
        letter = db.query(GeneratedLetter).filter(GeneratedLetter.id == letter_id).first()
        
        if not letter:
            raise LetterNotFoundException(letter_id=str(letter_id))
        
        # Verify firm-level isolation
        if letter.firm_id != firm_id:
            raise ForbiddenException(
                message="Access denied",
                detail="Letter does not belong to this firm",
            )
        
        # Validate at least one field is provided
        if title is None and content is None:
            from shared.exceptions import ValidationException
            raise ValidationException(
                message="At least one field (title or content) must be provided",
                detail="Both title and content cannot be None",
            )
        
        # Update fields
        if title is not None:
            letter.title = title
        if content is not None:
            letter.content = content
        
        # updated_at is automatically updated by the model's onupdate
        
        db.commit()
        db.refresh(letter)
        
        logger.info(f"Letter updated: {letter_id}")
        
        # Return updated letter using get_letter_by_id to get full data with joins
        return get_letter_by_id(db=db, letter_id=letter_id, firm_id=firm_id)
        
    except (LetterNotFoundException, ForbiddenException):
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating letter: {str(e)}")
        raise


def delete_letter(
    db: Session,
    letter_id: UUID,
    firm_id: UUID,
) -> None:
    """
    Delete a letter from S3 and database.
    
    Args:
        db: Database session
        letter_id: Letter ID
        firm_id: Firm ID to verify ownership
        
    Returns:
        None
        
    Raises:
        LetterNotFoundException: If letter not found
        ForbiddenException: If letter doesn't belong to firm
        S3UploadException: If S3 deletion fails
    """
    try:
        settings = get_settings()
        s3_client = get_s3_client()
        
        # Get letter and verify ownership
        letter = db.query(GeneratedLetter).filter(GeneratedLetter.id == letter_id).first()
        
        if not letter:
            raise LetterNotFoundException(letter_id=str(letter_id))
        
        # Verify firm-level isolation
        if letter.firm_id != firm_id:
            raise ForbiddenException(
                message="Access denied",
                detail="Letter does not belong to this firm",
            )
        
        # Delete .docx from S3 if exists
        if letter.docx_s3_key:
            try:
                s3_client.delete_file(
                    bucket_name=settings.aws.s3_bucket_exports,
                    s3_key=letter.docx_s3_key,
                )
                logger.info(f"Docx file deleted from S3: {letter.docx_s3_key}")
            except Exception as e:
                logger.error(f"Failed to delete docx file from S3: {str(e)}")
                raise S3UploadException(
                    message="Failed to delete .docx file from S3",
                    detail=str(e),
                )
        
        # Delete letter-document associations (cascade should handle this, but explicit for clarity)
        db.query(LetterSourceDocument).filter(
            LetterSourceDocument.letter_id == letter_id
        ).delete()
        
        # Delete letter from database
        db.delete(letter)
        db.commit()
        
        logger.info(f"Letter deleted: {letter_id}")
        
    except (LetterNotFoundException, ForbiddenException, S3UploadException):
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting letter: {str(e)}")
        raise


def finalize_letter(
    db: Session,
    letter_id: UUID,
    firm_id: UUID,
) -> LetterResponse:
    """
    Finalize a letter by generating DOCX and updating status to 'created'.
    Works on letters with status 'draft' OR 'created' (allows re-finalizing).
    Always generates new DOCX (overwrites existing if present).
    
    Args:
        db: Database session
        letter_id: Letter ID
        firm_id: Firm ID to verify ownership
        
    Returns:
        LetterResponse with finalized letter data and download URL
        
    Raises:
        LetterNotFoundException: If letter not found
        ForbiddenException: If letter doesn't belong to firm
        S3UploadException: If DOCX generation or upload fails
        ValueError: If HTML to DOCX conversion fails
    """
    try:
        settings = get_settings()
        s3_client = get_s3_client()
        
        # Get letter and verify ownership
        letter = db.query(GeneratedLetter).filter(GeneratedLetter.id == letter_id).first()
        
        if not letter:
            raise LetterNotFoundException(letter_id=str(letter_id))
        
        # Verify firm-level isolation
        if letter.firm_id != firm_id:
            raise ForbiddenException(
                message="Access denied",
                detail="Letter does not belong to this firm",
            )
        
        # Store old S3 key for cleanup if filename changes
        old_s3_key = letter.docx_s3_key
        
        # Generate filename
        filename = generate_filename(letter.title, letter.updated_at)
        new_s3_key = f"{firm_id}/letters/{filename}"
        
        # Convert HTML to DOCX
        try:
            doc = html_to_docx(letter.content)
        except Exception as e:
            logger.error(f"Failed to convert HTML to DOCX for letter {letter_id}: {str(e)}")
            raise ValueError(f"Failed to convert HTML to DOCX: {str(e)}") from e
        
        # Save DOCX to S3
        try:
            save_docx_to_s3(
                doc=doc,
                bucket_name=settings.aws.s3_bucket_exports,
                s3_key=new_s3_key,
                s3_client=s3_client,
            )
        except S3UploadException:
            raise
        except Exception as e:
            logger.error(f"Failed to save DOCX to S3 for letter {letter_id}: {str(e)}")
            raise S3UploadException(
                message="Failed to upload DOCX file to S3",
                detail=str(e),
            ) from e
        
        # Clean up old file if filename changed
        if old_s3_key and old_s3_key != new_s3_key:
            try:
                s3_client.delete_file(
                    bucket_name=settings.aws.s3_bucket_exports,
                    s3_key=old_s3_key,
                )
                logger.info(f"Cleaned up old DOCX file: {old_s3_key}")
            except Exception as e:
                logger.warning(f"Failed to delete old DOCX file {old_s3_key}: {str(e)}")
                # Don't fail the operation if cleanup fails
        
        # Update letter record
        letter.status = "created"
        letter.docx_s3_key = new_s3_key
        # updated_at is automatically updated by the model's onupdate
        
        db.commit()
        db.refresh(letter)
        
        logger.info(f"Letter finalized: {letter_id}, DOCX saved to {new_s3_key}")
        
        # Return updated letter with presigned URL
        return get_letter_by_id(db=db, letter_id=letter_id, firm_id=firm_id)
        
    except (LetterNotFoundException, ForbiddenException, S3UploadException, ValueError):
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error finalizing letter: {str(e)}")
        raise


def export_letter(
    db: Session,
    letter_id: UUID,
    firm_id: UUID,
) -> str:
    """
    Export a letter by always regenerating the DOCX from current letter content.
    This ensures re-export always uses the latest content, even if a DOCX already exists.
    Always generates a new DOCX, updates the database, and returns a new presigned URL.
    
    Args:
        db: Database session
        letter_id: Letter ID
        firm_id: Firm ID to verify ownership
        
    Returns:
        Presigned URL for downloading the DOCX file
        
    Raises:
        LetterNotFoundException: If letter not found
        ForbiddenException: If letter doesn't belong to firm
        S3UploadException: If DOCX generation or upload fails
        ValueError: If HTML to DOCX conversion fails
    """
    try:
        settings = get_settings()
        s3_client = get_s3_client()
        
        # Get letter and verify ownership
        letter = db.query(GeneratedLetter).filter(GeneratedLetter.id == letter_id).first()
        
        if not letter:
            raise LetterNotFoundException(letter_id=str(letter_id))
        
        # Verify firm-level isolation
        if letter.firm_id != firm_id:
            raise ForbiddenException(
                message="Access denied",
                detail="Letter does not belong to this firm",
            )
        
        # Always regenerate DOCX to ensure it reflects current letter content
        # Store old S3 key for cleanup
        old_s3_key = letter.docx_s3_key
        
        # Generate filename
        filename = generate_filename(letter.title, letter.updated_at)
        new_s3_key = f"{firm_id}/letters/{filename}"
        
        # Convert HTML to DOCX
        try:
            doc = html_to_docx(letter.content)
        except Exception as e:
            logger.error(f"Failed to convert HTML to DOCX for letter {letter_id}: {str(e)}")
            raise ValueError(f"Failed to convert HTML to DOCX: {str(e)}") from e
        
        # Save DOCX to S3
        try:
            save_docx_to_s3(
                doc=doc,
                bucket_name=settings.aws.s3_bucket_exports,
                s3_key=new_s3_key,
                s3_client=s3_client,
            )
        except S3UploadException:
            raise
        except Exception as e:
            logger.error(f"Failed to save DOCX to S3 for letter {letter_id}: {str(e)}")
            raise S3UploadException(
                message="Failed to upload DOCX file to S3",
                detail=str(e),
            ) from e
        
        # Always update docx_s3_key in database (may be new or updated)
        letter.docx_s3_key = new_s3_key
        # updated_at is automatically updated by the model's onupdate
        db.commit()
        db.refresh(letter)
        logger.info(f"Updated docx_s3_key for letter {letter_id}: {new_s3_key}")
        
        # Clean up old file if it exists and is different from new one
        if old_s3_key and old_s3_key != new_s3_key:
            try:
                s3_client.delete_file(
                    bucket_name=settings.aws.s3_bucket_exports,
                    s3_key=old_s3_key,
                )
                logger.info(f"Cleaned up old DOCX file: {old_s3_key}")
            except Exception as e:
                logger.warning(f"Failed to delete old DOCX file {old_s3_key}: {str(e)}")
                # Don't fail the operation if cleanup fails
        
        # Generate presigned URL
        try:
            presigned_url = s3_client.generate_presigned_url(
                bucket_name=settings.aws.s3_bucket_exports,
                s3_key=new_s3_key,
                expiration=3600,  # 1 hour
                http_method="GET",
            )
            logger.info(f"Generated new DOCX and URL for letter {letter_id}")
            return presigned_url
        except Exception as e:
            logger.error(f"Failed to generate presigned URL for new DOCX: {str(e)}")
            raise S3UploadException(
                message="Failed to generate download URL",
                detail=str(e),
            ) from e
        
    except (LetterNotFoundException, ForbiddenException, S3UploadException, ValueError):
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error exporting letter: {str(e)}")
        raise

