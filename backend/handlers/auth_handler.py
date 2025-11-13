"""
Lambda handler for auth service endpoints.
"""
from handlers.base import LambdaHandler
from services.auth_service.router import router
import logging

logger = logging.getLogger(__name__)

# Create the Lambda handler instance using the actual router
handler_instance = LambdaHandler(
    router=router,
    title="Auth Service API",
    description="API endpoints for authentication",
)

# Export the handler function for serverless.yml
handler = handler_instance

