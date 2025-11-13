"""
Lambda handler for template service endpoints.
"""
from handlers.base import LambdaHandler
from services.template_service.router import router
import logging

logger = logging.getLogger(__name__)

# Create the Lambda handler instance using the actual router
handler_instance = LambdaHandler(
    router=router,
    title="Template Service API",
    description="API endpoints for template management",
)

# Export the handler function for serverless.yml
handler = handler_instance

