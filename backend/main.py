"""
Main FastAPI application for local development.
This file is used for local development with uvicorn.
For Lambda deployment, each service has its own handler.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from shared.config import get_settings

app = FastAPI(
    title="Demand Letter Generator API",
    description="API for generating demand letters from legal documents",
    version="1.0.0",
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
    """Health check endpoint."""
    return {"status": "healthy"}


# Import and include routers from services
from services.document_service import router as document_router
from services.auth_service import router as auth_router
from shared.exceptions import register_exception_handlers

# Include routers
app.include_router(auth_router)
app.include_router(document_router)  # firm_id is in the router prefix

# Register exception handlers
register_exception_handlers(app)

# TODO: Add other service routers as they're implemented
# from services.template_service import router as template_router
# from services.letter_service import router as letter_router
# app.include_router(template_router)
# app.include_router(letter_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

