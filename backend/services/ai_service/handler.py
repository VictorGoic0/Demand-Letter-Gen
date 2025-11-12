"""
Lambda handler for AI service.
"""
from mangum import Mangum
from fastapi import FastAPI
from shared.exceptions import register_exception_handlers

from .router import router

# Create FastAPI app for this service
app = FastAPI(
    title="AI Service - Demand Letter Generator",
    description="AI service for generating demand letters",
    version="1.0.0",
)

# Include router
app.include_router(router)

# Register exception handlers
register_exception_handlers(app)


def generate_handler(event, context):
    """
    Lambda handler for letter generation endpoint.
    
    Configured with 60 second timeout for AI generation.
    """
    handler = Mangum(app, lifespan="off")
    return handler(event, context)

