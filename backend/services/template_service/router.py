"""
FastAPI router for template service endpoints.
"""
import logging
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from shared.database import get_db
from shared.exceptions import register_exception_handlers
from .schemas import (
    TemplateResponse,
    TemplateListResponse,
    TemplateCreate,
    TemplateUpdate,
)
from .logic import (
    create_template,
    get_templates,
    get_template_by_id,
    update_template,
    delete_template,
    get_default_template,
)

logger = logging.getLogger(__name__)

# Create router with firm_id in path (consistent with document_service)
router = APIRouter(prefix="/{firm_id}/templates", tags=["templates"])


@router.post(
    "/",
    response_model=TemplateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a template",
    description="Create a new letter template for a firm. If is_default=True, other default templates for the firm will be unset.",
)
async def create_template_endpoint(
    firm_id: UUID,
    template_data: TemplateCreate,
    created_by: Optional[UUID] = Query(None, description="User ID who created the template (optional)"),
    db: Session = Depends(get_db),
):
    """
    Create a new template.
    
    - **firm_id**: Firm ID (path parameter)
    - **template_data**: Template creation data (request body)
    - **created_by**: Optional user ID (query parameter)
    
    Returns template data on success.
    """
    try:
        template = create_template(
            db=db,
            firm_id=firm_id,
            created_by=created_by,
            template_data=template_data,
        )
        return template
        
    except Exception as e:
        logger.error(f"Error in create endpoint: {str(e)}")
        raise


@router.get(
    "/",
    response_model=TemplateListResponse,
    status_code=status.HTTP_200_OK,
    summary="List templates",
    description="Get a list of templates for a firm with optional sorting.",
)
async def list_templates_endpoint(
    firm_id: UUID,
    sort_by: Optional[str] = Query(None, description="Field to sort by (name, created_at)"),
    sort_order: str = Query("asc", description="Sort order (asc, desc)"),
    db: Session = Depends(get_db),
):
    """
    List templates for a firm.
    
    - **firm_id**: Firm ID (path parameter)
    - **sort_by**: Field to sort by (name, created_at)
    - **sort_order**: Sort order (asc, desc)
    
    Returns list of templates.
    """
    try:
        # Validate sort_by
        if sort_by and sort_by not in ["name", "created_at"]:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="sort_by must be 'name' or 'created_at'",
            )
        
        # Validate sort_order
        if sort_order not in ["asc", "desc"]:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="sort_order must be 'asc' or 'desc'",
            )
        
        # Get templates
        templates = get_templates(
            db=db,
            firm_id=firm_id,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        
        # Create paginated response (no pagination for templates, but use same response structure)
        return TemplateListResponse.create(
            items=templates,
            total=len(templates),
            page=1,
            page_size=len(templates),
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in list endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve templates",
        )


@router.get(
    "/default",
    response_model=TemplateResponse,
    status_code=status.HTTP_200_OK,
    summary="Get default template",
    description="Get the default template for a firm. Returns 404 if no default template exists.",
)
async def get_default_template_endpoint(
    firm_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get the default template for a firm.
    
    - **firm_id**: Firm ID (path parameter)
    
    Returns default template or 404 if not found.
    """
    try:
        template = get_default_template(
            db=db,
            firm_id=firm_id,
        )
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No default template found for this firm",
            )
        
        return template
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get default endpoint: {str(e)}")
        raise


@router.get(
    "/{template_id}",
    response_model=TemplateResponse,
    status_code=status.HTTP_200_OK,
    summary="Get template by ID",
    description="Get template metadata by ID, verifying it belongs to the firm.",
)
async def get_template_endpoint(
    firm_id: UUID,
    template_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get a template by ID.
    
    - **firm_id**: Firm ID (path parameter)
    - **template_id**: Template ID (path parameter)
    
    Returns template data.
    """
    try:
        template = get_template_by_id(
            db=db,
            template_id=template_id,
            firm_id=firm_id,
        )
        return template
        
    except Exception as e:
        logger.error(f"Error in get endpoint: {str(e)}")
        raise


@router.put(
    "/{template_id}",
    response_model=TemplateResponse,
    status_code=status.HTTP_200_OK,
    summary="Update template",
    description="Update a template, verifying it belongs to the firm. If is_default=True, other default templates for the firm will be unset.",
)
async def update_template_endpoint(
    firm_id: UUID,
    template_id: UUID,
    template_data: TemplateUpdate,
    db: Session = Depends(get_db),
):
    """
    Update a template.
    
    - **firm_id**: Firm ID (path parameter)
    - **template_id**: Template ID (path parameter)
    - **template_data**: Template update data (request body)
    
    Returns updated template data.
    """
    try:
        template = update_template(
            db=db,
            template_id=template_id,
            firm_id=firm_id,
            template_data=template_data,
        )
        return template
        
    except Exception as e:
        logger.error(f"Error in update endpoint: {str(e)}")
        raise


@router.delete(
    "/{template_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete template",
    description="Delete a template, verifying it belongs to the firm and is not in use by any letters.",
)
async def delete_template_endpoint(
    firm_id: UUID,
    template_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Delete a template.
    
    - **firm_id**: Firm ID (path parameter)
    - **template_id**: Template ID (path parameter)
    
    Returns 204 No Content on success, or 422 if template is in use.
    """
    try:
        delete_template(
            db=db,
            template_id=template_id,
            firm_id=firm_id,
        )
        return Response(status_code=status.HTTP_204_NO_CONTENT)
        
    except Exception as e:
        logger.error(f"Error in delete endpoint: {str(e)}")
        raise

