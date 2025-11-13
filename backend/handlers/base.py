"""
Base handler utility for wrapping FastAPI applications as Lambda handlers.
"""
from typing import Any, Dict
from mangum import Mangum
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

logger = logging.getLogger(__name__)


def create_lambda_app(
    router,
    title: str = "Demand Letter Generator API",
    description: str = "API endpoint for Demand Letter Generator",
    version: str = "1.0.0",
    cors_origins: list = None,
) -> FastAPI:
    """
    Create a FastAPI application configured for Lambda deployment.
    
    Args:
        router: FastAPI router to include
        title: Application title
        description: Application description
        version: Application version
        cors_origins: List of allowed CORS origins (defaults to all origins for Lambda)
        
    Returns:
        Configured FastAPI application
    """
    app = FastAPI(
        title=title,
        description=description,
        version=version,
    )
    
    # Configure CORS - allow all origins for Lambda/API Gateway
    # In production, you may want to restrict this to specific domains
    if cors_origins is None:
        cors_origins = ["*"]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include the router
    app.include_router(router)
    
    return app


def create_handler(app: FastAPI) -> Mangum:
    """
    Create a Mangum handler for a FastAPI application.
    
    Args:
        app: FastAPI application instance
        
    Returns:
        Mangum handler instance
    """
    import os
    # Get stage from environment (set by Serverless Framework)
    stage = os.getenv("SERVERLESS_STAGE", os.getenv("STAGE", "dev"))
    api_gateway_base_path = f"/{stage}"
    
    return Mangum(
        app,
        lifespan="off",  # Disable lifespan events for Lambda
        api_gateway_base_path=api_gateway_base_path,
    )


class LambdaHandler:
    """
    Base class for Lambda handlers.
    
    This class provides a consistent pattern for creating Lambda handlers
    that wrap FastAPI routers.
    """
    
    def __init__(
        self,
        router,
        title: str = "Demand Letter Generator API",
        description: str = "API endpoint for Demand Letter Generator",
        version: str = "1.0.0",
        cors_origins: list = None,
    ):
        """
        Initialize the Lambda handler.
        
        Args:
            router: FastAPI router to wrap
            title: Application title
            description: Application description
            version: Application version
            cors_origins: List of allowed CORS origins
        """
        self.app = create_lambda_app(
            router=router,
            title=title,
            description=description,
            version=version,
            cors_origins=cors_origins,
        )
        self.handler = create_handler(self.app)
    
    def __call__(self, event: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """
        Handle Lambda invocation.
        
        Args:
            event: Lambda event dictionary
            context: Lambda context object
            
        Returns:
            Response dictionary
        """
        try:
            logger.info(f"Lambda handler invoked: {event.get('path', 'unknown')}")
            response = self.handler(event, context)
            return response
        except Exception as e:
            logger.error(f"Error in Lambda handler: {str(e)}", exc_info=True)
            return {
                "statusCode": 500,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
                "body": '{"error": "Internal server error"}',
            }

