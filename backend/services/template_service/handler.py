"""
Lambda handler for template service.
"""
import logging
from handlers.base import create_lambda_app, create_handler
from shared.exceptions import register_exception_handlers
from .router import router

logger = logging.getLogger(__name__)

# Create FastAPI app with router
app = create_lambda_app(
    router=router,
    title="Template Service API",
    description="API endpoint for template management",
    version="1.0.0",
)

# Register exception handlers
register_exception_handlers(app)

# Create Mangum handler
handler = create_handler(app)


def create_handler_func(event, context):
    """Lambda handler for template creation."""
    return handler(event, context)


def list_handler_func(event, context):
    """Lambda handler for template listing."""
    return handler(event, context)


def get_default_handler_func(event, context):
    """Lambda handler for getting default template."""
    return handler(event, context)


def get_handler_func(event, context):
    """Lambda handler for getting a template."""
    return handler(event, context)


def update_handler_func(event, context):
    """Lambda handler for updating a template."""
    return handler(event, context)


def delete_handler_func(event, context):
    """Lambda handler for deleting a template."""
    return handler(event, context)

