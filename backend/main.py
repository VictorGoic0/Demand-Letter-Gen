"""
Main FastAPI application for local development.
This file is used for local development with uvicorn.
For Lambda deployment, each service has its own handler.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from shared.config import get_settings
from shared.database import engine, SessionLocal
from shared.s3_client import get_s3_client

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    Performs detailed health checks on startup.
    """
    # Startup: Check database connection
    logger.info("Starting up application...")
    try:
        if engine is None:
            raise RuntimeError("Database engine is not initialized")
        
        # Test database connection with a simple query
        db = SessionLocal()
        try:
            db.execute(text("SELECT 1"))
            logger.info("✅ Database connection successful")
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise
        finally:
            db.close()
    except Exception as e:
        logger.error(f"❌ Database health check failed: {e}")
        raise
    
    # Startup: Check S3 buckets
    try:
        settings = get_settings()
        s3_client = get_s3_client()
        
        # Check documents bucket
        documents_bucket = settings.aws.s3_bucket_documents
        if s3_client.check_bucket_exists(documents_bucket):
            logger.info(f"✅ S3 documents bucket accessible: {documents_bucket}")
        else:
            logger.warning(f"⚠️  S3 documents bucket not accessible: {documents_bucket}")
        
        # Check exports bucket
        exports_bucket = settings.aws.s3_bucket_exports
        if s3_client.check_bucket_exists(exports_bucket):
            logger.info(f"✅ S3 exports bucket accessible: {exports_bucket}")
        else:
            logger.warning(f"⚠️  S3 exports bucket not accessible: {exports_bucket}")
    except Exception as e:
        logger.error(f"❌ S3 health check failed: {e}")
        # Don't raise - S3 might not be critical for local dev
    
    logger.info("✅ Application startup complete")
    
    yield
    
    # Shutdown: Cleanup
    logger.info("Shutting down application...")
    try:
        if engine:
            engine.dispose()
            logger.info("✅ Database connections closed")
    except Exception as e:
        logger.error(f"❌ Error during shutdown: {e}")
    logger.info("✅ Application shutdown complete")


app = FastAPI(
    title="Demand Letter Generator API",
    description="API for generating demand letters from legal documents",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS from settings
# For development, allow all origins by default (can be overridden via CORS_ALLOW_ORIGINS env var)
settings = get_settings()
cors_config = settings.cors

# Handle wildcard origins
# Note: FastAPI doesn't allow ["*"] with allow_credentials=True, so we use a list of common dev origins
cors_origins = cors_config.allow_origins
if cors_origins == ["*"] or (len(cors_origins) == 1 and cors_origins[0] == "*"):
    # For development, allow common localhost origins
    # In production, you should specify exact origins
    cors_origins = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:8080",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=cors_config.allow_credentials,
    allow_methods=["*"] if cors_config.allow_methods == ["*"] else cors_config.allow_methods,
    allow_headers=["*"] if cors_config.allow_headers == ["*"] else cors_config.allow_headers,
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Demand Letter Generator API", "status": "healthy"}


@app.get("/health")
async def health():
    """
    Detailed health check endpoint.
    Returns status of database and S3 connections.
    """
    health_status = {
        "status": "healthy",
        "database": "unknown",
        "s3": "unknown",
    }
    
    # Check database
    try:
        if engine is None:
            health_status["database"] = "error"
            health_status["status"] = "unhealthy"
        else:
            db = SessionLocal()
            try:
                db.execute(text("SELECT 1"))
                health_status["database"] = "connected"
            except Exception as e:
                health_status["database"] = f"error: {str(e)}"
                health_status["status"] = "unhealthy"
            finally:
                db.close()
    except Exception as e:
        health_status["database"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Check S3
    try:
        settings = get_settings()
        s3_client = get_s3_client()
        
        documents_ok = s3_client.check_bucket_exists(settings.aws.s3_bucket_documents)
        exports_ok = s3_client.check_bucket_exists(settings.aws.s3_bucket_exports)
        
        if documents_ok and exports_ok:
            health_status["s3"] = "connected"
        elif documents_ok or exports_ok:
            health_status["s3"] = "partial"
        else:
            health_status["s3"] = "error"
    except Exception as e:
        health_status["s3"] = f"error: {str(e)}"
    
    return health_status


# Import and include routers from services
from services.document_service import router as document_router
from services.auth_service import router as auth_router
from services.template_service import router as template_router
from services.parser_service import router as parser_router
from services.ai_service import router as ai_router
from services.letter_service import router as letter_router
from shared.exceptions import register_exception_handlers

# Include routers
app.include_router(auth_router)
app.include_router(document_router)  # firm_id is in the router prefix
app.include_router(template_router)  # firm_id is in the router prefix
app.include_router(parser_router, prefix="/parse")  # firm_id is query param
app.include_router(ai_router)  # firm_id is query param
app.include_router(letter_router)  # firm_id is in the router prefix

# Register exception handlers
register_exception_handlers(app)


# Lambda health handler
def health_handler(event, context):
    """
    Simple health check handler for Lambda.
    Returns basic health status without database/S3 checks for faster response.
    """
    import json
    import os
    
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps({
            "status": "healthy",
            "service": "demand-letter-generator",
            "environment": os.getenv("ENVIRONMENT", "unknown"),
        })
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

