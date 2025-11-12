"""
Business logic for AI service letter generation operations.
"""
import logging
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from shared.models.document import Document
from shared.models.template import LetterTemplate
from shared.models.letter import GeneratedLetter
from shared.models.letter_document import LetterSourceDocument
from shared.exceptions import (
    DocumentNotFoundException,
    TemplateNotFoundException,
    ForbiddenException,
    ValidationException,
    OpenAIException,
    ParserException,
)
from shared.utils import sanitize_html
from .schemas import GenerateRequest, GenerateResponse
from .openai_client import call_openai_api, build_generation_prompt, validate_response_format
from services.parser_service.logic import parse_document
from services.template_service.logic import get_template_by_id

logger = logging.getLogger(__name__)


def generate_letter(
    db: Session,
    firm_id: UUID,
    created_by: Optional[UUID],
    request: GenerateRequest,
) -> GenerateResponse:
    """
    Generate a demand letter using AI from template and documents.
    
    Args:
        db: Database session
        firm_id: Firm ID that owns the letter
        created_by: Optional user ID who is creating the letter
        request: GenerateRequest with template_id, document_ids, and optional title
        
    Returns:
        GenerateResponse with letter_id, content, and status
        
    Raises:
        ValidationException: If document count is invalid or documents are empty
        TemplateNotFoundException: If template not found
        ForbiddenException: If template or documents don't belong to firm
        DocumentNotFoundException: If any document not found
        ParserException: If document parsing fails
        OpenAIException: If OpenAI API call fails
    """
    try:
        # Validate document count (already validated in schema, but double-check)
        if len(request.document_ids) == 0:
            raise ValidationException(
                message="At least one document is required",
                detail="document_ids list cannot be empty",
            )
        if len(request.document_ids) > 5:
            raise ValidationException(
                message="Too many documents",
                detail="Maximum 5 documents allowed per letter generation",
            )
        
        logger.info(f"Starting letter generation for firm {firm_id} with template {request.template_id} and {len(request.document_ids)} documents")
        
        # Fetch and verify template
        try:
            template_response = get_template_by_id(
                db=db,
                template_id=request.template_id,
                firm_id=firm_id,
            )
        except (TemplateNotFoundException, ForbiddenException):
            raise
        except Exception as e:
            logger.error(f"Error fetching template: {str(e)}")
            raise TemplateNotFoundException(
                template_id=str(request.template_id),
                detail=f"Failed to fetch template: {str(e)}",
            )
        
        # Convert template response to dict for prompt building
        template_data = {
            "letterhead_text": template_response.letterhead_text,
            "opening_paragraph": template_response.opening_paragraph,
            "closing_paragraph": template_response.closing_paragraph,
            "sections": template_response.sections or [],
        }
        
        # Fetch and verify all documents
        documents = []
        for doc_id in request.document_ids:
            document = db.query(Document).filter(Document.id == doc_id).first()
            
            if not document:
                raise DocumentNotFoundException(document_id=str(doc_id))
            
            # Verify firm-level isolation
            if document.firm_id != firm_id:
                raise ForbiddenException(
                    message="Access denied",
                    detail=f"Document {doc_id} does not belong to this firm",
                )
            
            documents.append(document)
        
        logger.info(f"Fetched {len(documents)} documents for parsing")
        
        # Parse all documents
        parsed_documents = []
        for document in documents:
            try:
                parse_response = parse_document(
                    db=db,
                    document_id=document.id,
                    firm_id=firm_id,
                )
                
                # Validate extracted text is not empty
                if not parse_response.extracted_text or not parse_response.extracted_text.strip():
                    logger.warning(f"Document {document.id} has empty extracted text")
                    raise ValidationException(
                        message="Document has no extractable text",
                        detail=f"Document {document.filename} could not be parsed or contains no text",
                    )
                
                parsed_documents.append({
                    "document_id": str(document.id),
                    "extracted_text": parse_response.extracted_text,
                    "page_count": parse_response.page_count,
                    "file_size": parse_response.file_size,
                    "metadata": parse_response.metadata,
                })
                
            except (DocumentNotFoundException, ForbiddenException, ParserException):
                raise
            except ValidationException:
                raise
            except Exception as e:
                logger.error(f"Error parsing document {document.id}: {str(e)}")
                raise ParserException(
                    message="Failed to parse document",
                    detail=f"Error parsing document {document.filename}: {str(e)}",
                )
        
        if len(parsed_documents) == 0:
            raise ValidationException(
                message="No valid documents to process",
                detail="All documents failed to parse or contain no text",
            )
        
        logger.info(f"Successfully parsed {len(parsed_documents)} documents")
        
        # Build prompt
        try:
            messages = build_generation_prompt(
                template_data=template_data,
                parsed_documents=parsed_documents,
            )
        except Exception as e:
            logger.error(f"Error building prompt: {str(e)}")
            raise ValidationException(
                message="Failed to build generation prompt",
                detail=str(e),
            )
        
        # Call OpenAI API
        try:
            generated_content = call_openai_api(messages=messages)
        except OpenAIException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error calling OpenAI API: {str(e)}")
            raise OpenAIException(
                message="Failed to generate letter",
                detail=f"Unexpected error: {str(e)}",
            )
        
        # Validate response format
        if not validate_response_format(generated_content):
            logger.warning("OpenAI response does not appear to be valid HTML, but continuing")
        
        # Sanitize HTML output
        sanitized_content = sanitize_html(generated_content)
        
        if not sanitized_content or not sanitized_content.strip():
            raise ValidationException(
                message="Generated content is empty",
                detail="OpenAI returned empty or invalid content",
            )
        
        # Generate title if not provided
        title = request.title
        if not title or not title.strip():
            title = f"Demand Letter - {template_response.name}"
        
        # Create letter record in database
        try:
            letter = GeneratedLetter(
                firm_id=firm_id,
                created_by=created_by,
                title=title[:255],  # Ensure title fits in column
                content=sanitized_content,
                status="draft",
                template_id=request.template_id,
            )
            
            db.add(letter)
            db.flush()  # Flush to get letter.id before creating associations
            
            # Create letter-document associations
            for document in documents:
                association = LetterSourceDocument(
                    letter_id=letter.id,
                    document_id=document.id,
                )
                db.add(association)
            
            db.commit()
            db.refresh(letter)
            
            logger.info(f"Successfully generated letter {letter.id} for firm {firm_id}")
            
            return GenerateResponse(
                letter_id=letter.id,
                content=letter.content,
                status=letter.status,
            )
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating letter record: {str(e)}")
            raise ValidationException(
                message="Failed to save generated letter",
                detail=f"Database error: {str(e)}",
            )
        
    except (
        ValidationException,
        TemplateNotFoundException,
        ForbiddenException,
        DocumentNotFoundException,
        ParserException,
        OpenAIException,
    ):
        raise
    except Exception as e:
        logger.error(f"Unexpected error generating letter: {str(e)}")
        raise ValidationException(
            message="Failed to generate letter",
            detail=f"Unexpected error: {str(e)}",
        )

