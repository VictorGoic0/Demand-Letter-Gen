"""
Lambda handler for document service.
"""
import logging
from handlers.base import create_lambda_app, create_handler
from shared.exceptions import register_exception_handlers
from .router import router

logger = logging.getLogger(__name__)

# Create FastAPI app with router
app = create_lambda_app(
    router=router,
    title="Document Service API",
    description="API endpoint for document upload and management",
    version="1.0.0",
)

# Register exception handlers
register_exception_handlers(app)

# Create Mangum handler
handler = create_handler(app)


def upload_handler(event, context):
    """Lambda handler for document upload."""
    return handler(event, context)


def list_handler(event, context):
    """Lambda handler for document listing."""
    return handler(event, context)


def get_handler(event, context):
    """Lambda handler for getting a document."""
    return handler(event, context)


def delete_handler(event, context):
    """Lambda handler for deleting a document."""
    return handler(event, context)


def download_handler(event, context):
    """Lambda handler for generating download URL."""
    return handler(event, context)

