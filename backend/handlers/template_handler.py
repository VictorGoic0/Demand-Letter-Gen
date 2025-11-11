"""
Lambda handler for template service endpoints.
"""
from fastapi import APIRouter
from handlers.base import LambdaHandler
import logging

logger = logging.getLogger(__name__)

# Create a router for template endpoints
# TODO: Import actual router from template_service when implemented
router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("/")
async def list_templates():
    """List all templates."""
    # Placeholder - will be implemented when template_service is created
    return {"message": "Template list endpoint - to be implemented"}


@router.post("/")
async def create_template():
    """Create a new template."""
    # Placeholder - will be implemented when template_service is created
    return {"message": "Template creation endpoint - to be implemented"}


@router.get("/{template_id}")
async def get_template(template_id: str):
    """Get a specific template."""
    # Placeholder - will be implemented when template_service is created
    return {"message": f"Get template {template_id} - to be implemented"}


# Create the Lambda handler instance
handler_instance = LambdaHandler(
    router=router,
    title="Template Service API",
    description="API endpoints for template management",
)

# Export the handler function for serverless.yml
handler = handler_instance

