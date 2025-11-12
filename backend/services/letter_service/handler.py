"""
Lambda handler for letter service.
"""
from mangum import Mangum
from fastapi import FastAPI
from shared.exceptions import register_exception_handlers

from .router import router

# Create FastAPI app for this service
app = FastAPI(
    title="Letter Service - Demand Letter Generator",
    description="Letter service for managing generated demand letters",
    version="1.0.0",
)

# Include router
app.include_router(router)

# Register exception handlers
register_exception_handlers(app)


def list_handler(event, context):
    """
    Lambda handler for list letters endpoint.
    """
    handler = Mangum(app, lifespan="off")
    return handler(event, context)


def get_handler(event, context):
    """
    Lambda handler for get letter endpoint.
    """
    handler = Mangum(app, lifespan="off")
    return handler(event, context)


def update_handler(event, context):
    """
    Lambda handler for update letter endpoint.
    """
    handler = Mangum(app, lifespan="off")
    return handler(event, context)


def delete_handler(event, context):
    """
    Lambda handler for delete letter endpoint.
    """
    handler = Mangum(app, lifespan="off")
    return handler(event, context)


def finalize_handler(event, context):
    """
    Lambda handler for finalize letter endpoint.
    """
    handler = Mangum(app, lifespan="off")
    return handler(event, context)


def export_handler(event, context):
    """
    Lambda handler for export letter endpoint.
    """
    handler = Mangum(app, lifespan="off")
    return handler(event, context)

