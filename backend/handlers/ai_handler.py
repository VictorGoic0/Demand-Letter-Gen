"""
Lambda handler for AI service endpoints.
"""
from handlers.base import LambdaHandler
from services.ai_service.router import router
import logging

logger = logging.getLogger(__name__)

# Create the Lambda handler instance using the actual router
handler_instance = LambdaHandler(
    router=router,
    title="AI Service API",
    description="API endpoints for AI letter generation",
)

# Export the handler function for serverless.yml
handler = handler_instance

