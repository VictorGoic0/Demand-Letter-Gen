"""
Business logic for parser service operations.
"""
import logging
import io
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from shared.models.document import Document
from shared.exceptions import (
    DocumentNotFoundException,
    S3DownloadException,
    ForbiddenException,
    ParserException,
)
from shared.s3_client import get_s3_client
from shared.config import get_settings
from .pdf_parser import extract_text_from_pdf, extract_metadata_from_pdf
from .schemas import ParseResponse

logger = logging.getLogger(__name__)


def parse_document(
    db: Session,
    document_id: UUID,
    firm_id: UUID,
) -> ParseResponse:
    """
    Parse a single document by downloading it from S3 and extracting text.
    
    Args:
        db: Database session
        document_id: Document ID to parse
        firm_id: Firm ID to verify ownership
        
    Returns:
        ParseResponse with extracted text and metadata
        
    Raises:
        DocumentNotFoundException: If document not found
        ForbiddenException: If document doesn't belong to firm
        S3DownloadException: If S3 download fails
        ParserException: If PDF parsing fails
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
        
        # Verify document is a PDF
        if document.mime_type != "application/pdf":
            raise ParserException(
                message="Unsupported file type",
                detail=f"Only PDF files can be parsed. Document type: {document.mime_type}",
            )
        
        # Download file from S3 to memory
        try:
            file_obj = io.BytesIO()
            s3_client.download_fileobj(
                bucket_name=settings.aws.s3_bucket_documents,
                s3_key=document.s3_key,
                file_obj=file_obj,
            )
            file_content = file_obj.getvalue()
            logger.info(f"Downloaded document from S3: {document.s3_key}")
        except Exception as e:
            logger.error(f"Failed to download document from S3: {str(e)}")
            raise S3DownloadException(
                message="Failed to download document from S3",
                detail=str(e),
            )
        
        # Extract text from PDF
        try:
            extracted_text = extract_text_from_pdf(file_content)
        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {str(e)}")
            raise ParserException(
                message="Failed to extract text from PDF",
                detail=str(e),
            )
        
        # Extract metadata from PDF
        try:
            metadata = extract_metadata_from_pdf(file_content)
        except Exception as e:
            logger.warning(f"Failed to extract metadata from PDF: {str(e)}")
            # Metadata extraction failure is not critical, use basic info
            metadata = {
                "page_count": 0,
                "file_size": document.file_size,
                "creation_date": None,
                "modification_date": None,
            }
        
        # Build response
        return ParseResponse(
            document_id=document_id,
            extracted_text=extracted_text,
            page_count=metadata.get("page_count", 0),
            file_size=metadata.get("file_size", document.file_size),
            metadata=metadata,
            success=True,
            error=None,
        )
        
    except (DocumentNotFoundException, ForbiddenException, S3DownloadException, ParserException):
        raise
    except Exception as e:
        logger.error(f"Error parsing document: {str(e)}")
        raise ParserException(
            message="Failed to parse document",
            detail=str(e),
        )


def parse_documents_batch(
    db: Session,
    document_ids: List[UUID],
    firm_id: UUID,
) -> List[ParseResponse]:
    """
    Parse multiple documents in batch.
    
    Args:
        db: Database session
        document_ids: List of document IDs to parse
        firm_id: Firm ID to verify ownership
        
    Returns:
        List of ParseResponse objects (one per document)
        
    Raises:
        DocumentNotFoundException: If any document not found
        ForbiddenException: If any document doesn't belong to firm
    """
    try:
        results = []
        
        # Process each document
        for document_id in document_ids:
            try:
                result = parse_document(
                    db=db,
                    document_id=document_id,
                    firm_id=firm_id,
                )
                results.append(result)
                
            except (DocumentNotFoundException, ForbiddenException) as e:
                # For batch operations, we include failed results in the response
                logger.warning(f"Failed to parse document {document_id}: {str(e)}")
                results.append(
                    ParseResponse(
                        document_id=document_id,
                        extracted_text="",
                        page_count=0,
                        file_size=0,
                        metadata=None,
                        success=False,
                        error=str(e),
                    )
                )
            except Exception as e:
                # Include parsing errors in results
                logger.error(f"Error parsing document {document_id}: {str(e)}")
                results.append(
                    ParseResponse(
                        document_id=document_id,
                        extracted_text="",
                        page_count=0,
                        file_size=0,
                        metadata=None,
                        success=False,
                        error=str(e),
                    )
                )
        
        logger.info(f"Batch parsing completed: {len(results)} documents processed")
        return results
        
    except Exception as e:
        logger.error(f"Error in batch parsing: {str(e)}")
        raise

