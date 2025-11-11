"""
Lambda handler for document service endpoints.
"""
from fastapi import APIRouter
from handlers.base import LambdaHandler
import logging

logger = logging.getLogger(__name__)

# Create a router for document endpoints
# TODO: Import actual router from document_service when implemented
router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("/")
async def list_documents():
    """List all documents."""
    # Placeholder - will be implemented when document_service is created
    return {"message": "Document list endpoint - to be implemented"}


@router.post("/upload")
async def upload_document():
    """Upload a document."""
    # Placeholder - will be implemented when document_service is created
    return {"message": "Document upload endpoint - to be implemented"}


@router.get("/{document_id}")
async def get_document(document_id: str):
    """Get a specific document."""
    # Placeholder - will be implemented when document_service is created
    return {"message": f"Get document {document_id} - to be implemented"}


# Create the Lambda handler instance
handler_instance = LambdaHandler(
    router=router,
    title="Document Service API",
    description="API endpoints for document management",
)

# Export the handler function for serverless.yml
handler = handler_instance

