"""
Main FastAPI application for local development.
This file is used for local development with uvicorn.
For Lambda deployment, each service has its own handler.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Demand Letter Generator API",
    description="API for generating demand letters from legal documents",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Demand Letter Generator API", "status": "healthy"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


# TODO: Import and include routers from services
# from services.document_service import router as document_router
# from services.template_service import router as template_router
# from services.letter_service import router as letter_router
#
# app.include_router(document_router, prefix="/documents", tags=["documents"])
# app.include_router(template_router, prefix="/templates", tags=["templates"])
# app.include_router(letter_router, prefix="/letters", tags=["letters"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

