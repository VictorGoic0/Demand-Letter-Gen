"""
Lambda handler for letter service endpoints.
"""

import logging

from handlers.base import LambdaHandler
from services.letter_service.router import router

logger = logging.getLogger(__name__)

# Create the Lambda handler instance using the actual router
handler_instance = LambdaHandler(
    router=router,
    title="Letter Service API",
    description="API endpoints for letter generation and management",
)

# Export the handler function for serverless.yml
handler = handler_instance
