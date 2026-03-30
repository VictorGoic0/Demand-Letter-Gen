"""
Lambda handler for document service endpoints.
"""

import logging

from handlers.base import LambdaHandler
from services.document_service.router import router

logger = logging.getLogger(__name__)

# Create the Lambda handler instance using the actual router
handler_instance = LambdaHandler(
    router=router,
    title="Document Service API",
    description="API endpoints for document management",
)

# Export the handler function for serverless.yml
handler = handler_instance
