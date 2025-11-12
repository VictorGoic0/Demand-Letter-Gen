"""
Business logic for template service operations.
"""
import logging
from typing import Optional, List, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc

from shared.models.template import LetterTemplate
from shared.models.letter import GeneratedLetter
from shared.exceptions import (
    TemplateNotFoundException,
    ForbiddenException,
    ValidationException,
)
from .schemas import TemplateResponse, TemplateCreate, TemplateUpdate

logger = logging.getLogger(__name__)


def create_template(
    db: Session,
    firm_id: UUID,
    created_by: Optional[UUID],
    template_data: TemplateCreate,
) -> TemplateResponse:
    """
    Create a new template for a firm.
    
    Args:
        db: Database session
        firm_id: Firm ID that owns the template
        created_by: Optional user ID who created the template
        template_data: Template creation data
        
    Returns:
        TemplateResponse with template data
        
    Raises:
        ValidationException: If template data is invalid
    """
    try:
        # If is_default=True, unset other defaults for the firm
        if template_data.is_default:
            db.query(LetterTemplate).filter(
                LetterTemplate.firm_id == firm_id,
                LetterTemplate.is_default == True,
            ).update({"is_default": False})
            db.flush()  # Flush to apply update before commit
        
        # Create new template
        template = LetterTemplate(
            firm_id=firm_id,
            created_by=created_by,
            name=template_data.name,
            letterhead_text=template_data.letterhead_text,
            opening_paragraph=template_data.opening_paragraph,
            closing_paragraph=template_data.closing_paragraph,
            sections=template_data.sections,  # JSONB field accepts list
            is_default=template_data.is_default,
        )
        
        db.add(template)
        db.commit()
        db.refresh(template)
        
        logger.info(f"Template created: {template.id} for firm {firm_id}")
        
        return TemplateResponse.model_validate(template)
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating template: {str(e)}")
        raise


def get_templates(
    db: Session,
    firm_id: UUID,
    sort_by: Optional[str] = None,
    sort_order: str = "asc",
) -> List[TemplateResponse]:
    """
    Get list of templates for a firm.
    
    Args:
        db: Database session
        firm_id: Firm ID to filter templates
        sort_by: Field to sort by (name, created_at)
        sort_order: Sort order (asc, desc)
        
    Returns:
        List of TemplateResponse
    """
    try:
        # Base query filtered by firm_id
        query = db.query(LetterTemplate).filter(LetterTemplate.firm_id == firm_id)
        
        # Apply sorting
        if sort_by == "name":
            order_func = asc(LetterTemplate.name) if sort_order == "asc" else desc(LetterTemplate.name)
        elif sort_by == "created_at" or sort_by is None:
            order_func = asc(LetterTemplate.created_at) if sort_order == "asc" else desc(LetterTemplate.created_at)
        else:
            # Default to name asc
            order_func = asc(LetterTemplate.name)
        
        query = query.order_by(order_func)
        
        # Get all templates (no pagination for templates - typically small number)
        templates = query.all()
        
        # Convert to response models
        template_responses = [TemplateResponse.model_validate(t) for t in templates]
        
        logger.info(f"Retrieved {len(template_responses)} templates for firm {firm_id}")
        
        return template_responses
        
    except Exception as e:
        logger.error(f"Error getting templates: {str(e)}")
        raise


def get_template_by_id(
    db: Session,
    template_id: UUID,
    firm_id: UUID,
) -> TemplateResponse:
    """
    Get a template by ID, verifying it belongs to the firm.
    
    Args:
        db: Database session
        template_id: Template ID
        firm_id: Firm ID to verify ownership
        
    Returns:
        TemplateResponse with template data
        
    Raises:
        TemplateNotFoundException: If template not found
        ForbiddenException: If template doesn't belong to firm
    """
    try:
        template = db.query(LetterTemplate).filter(LetterTemplate.id == template_id).first()
        
        if not template:
            raise TemplateNotFoundException(template_id=str(template_id))
        
        # Verify firm-level isolation
        if template.firm_id != firm_id:
            raise ForbiddenException(
                message="Access denied",
                detail="Template does not belong to this firm",
            )
        
        return TemplateResponse.model_validate(template)
        
    except (TemplateNotFoundException, ForbiddenException):
        raise
    except Exception as e:
        logger.error(f"Error getting template: {str(e)}")
        raise


def update_template(
    db: Session,
    template_id: UUID,
    firm_id: UUID,
    template_data: TemplateUpdate,
) -> TemplateResponse:
    """
    Update a template, verifying it belongs to the firm.
    
    Args:
        db: Database session
        template_id: Template ID
        firm_id: Firm ID to verify ownership
        template_data: Template update data
        
    Returns:
        TemplateResponse with updated template data
        
    Raises:
        TemplateNotFoundException: If template not found
        ForbiddenException: If template doesn't belong to firm
    """
    try:
        # Get template and verify ownership
        template = db.query(LetterTemplate).filter(LetterTemplate.id == template_id).first()
        
        if not template:
            raise TemplateNotFoundException(template_id=str(template_id))
        
        # Verify firm-level isolation
        if template.firm_id != firm_id:
            raise ForbiddenException(
                message="Access denied",
                detail="Template does not belong to this firm",
            )
        
        # If is_default=True, unset other defaults for the firm
        if template_data.is_default is True:
            db.query(LetterTemplate).filter(
                LetterTemplate.firm_id == firm_id,
                LetterTemplate.id != template_id,
                LetterTemplate.is_default == True,
            ).update({"is_default": False})
            db.flush()
        
        # Update fields (only update provided fields)
        update_dict = template_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(template, key, value)
        
        db.commit()
        db.refresh(template)
        
        logger.info(f"Template updated: {template_id}")
        
        return TemplateResponse.model_validate(template)
        
    except (TemplateNotFoundException, ForbiddenException):
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating template: {str(e)}")
        raise


def delete_template(
    db: Session,
    template_id: UUID,
    firm_id: UUID,
) -> None:
    """
    Delete a template, verifying it belongs to the firm and is not in use.
    
    Args:
        db: Database session
        template_id: Template ID
        firm_id: Firm ID to verify ownership
        
    Returns:
        None
        
    Raises:
        TemplateNotFoundException: If template not found
        ForbiddenException: If template doesn't belong to firm
        ValidationException: If template is in use by letters
    """
    try:
        # Get template and verify ownership
        template = db.query(LetterTemplate).filter(LetterTemplate.id == template_id).first()
        
        if not template:
            raise TemplateNotFoundException(template_id=str(template_id))
        
        # Verify firm-level isolation
        if template.firm_id != firm_id:
            raise ForbiddenException(
                message="Access denied",
                detail="Template does not belong to this firm",
            )
        
        # Check if template is in use by letters
        letters_count = db.query(GeneratedLetter).filter(
            GeneratedLetter.template_id == template_id,
        ).count()
        
        if letters_count > 0:
            raise ValidationException(
                message="Cannot delete template",
                detail=f"Template is in use by {letters_count} letter(s). Please delete or update those letters first.",
            )
        
        # Delete template
        db.delete(template)
        db.commit()
        
        logger.info(f"Template deleted: {template_id}")
        
    except (TemplateNotFoundException, ForbiddenException, ValidationException):
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting template: {str(e)}")
        raise


def get_default_template(
    db: Session,
    firm_id: UUID,
) -> Optional[TemplateResponse]:
    """
    Get the default template for a firm.
    
    Args:
        db: Database session
        firm_id: Firm ID to filter templates
        
    Returns:
        TemplateResponse if default template exists, None otherwise
    """
    try:
        template = db.query(LetterTemplate).filter(
            LetterTemplate.firm_id == firm_id,
            LetterTemplate.is_default == True,
        ).first()
        
        if not template:
            return None
        
        return TemplateResponse.model_validate(template)
        
    except Exception as e:
        logger.error(f"Error getting default template: {str(e)}")
        raise

