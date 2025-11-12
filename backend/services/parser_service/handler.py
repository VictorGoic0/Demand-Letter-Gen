"""
Lambda handler for parser service.
"""
import logging
from handlers.base import create_lambda_app, create_handler
from shared.exceptions import register_exception_handlers
from .router import router

logger = logging.getLogger(__name__)

# Create FastAPI app with router
app = create_lambda_app(
    router=router,
    title="Parser Service API",
    description="API endpoint for PDF document parsing",
    version="1.0.0",
)

# Register exception handlers
register_exception_handlers(app)

# Create Mangum handler
handler = create_handler(app)


def parse_handler(event, context):
    """Lambda handler for document parsing."""
    return handler(event, context)


def batch_handler(event, context):
    """Lambda handler for batch document parsing."""
    return handler(event, context)

