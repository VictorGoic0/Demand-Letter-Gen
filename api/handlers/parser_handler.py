"""
Lambda handler for parser service endpoints.
"""

import logging

from handlers.base import LambdaHandler
from services.parser_service.router import router

logger = logging.getLogger(__name__)

# Create the Lambda handler instance using the actual router
handler_instance = LambdaHandler(
    router=router,
    title="Parser Service API",
    description="API endpoints for document parsing",
)

# Export the handler function for serverless.yml
handler = handler_instance
