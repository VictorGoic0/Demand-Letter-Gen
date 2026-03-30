"""
Parser service for extracting text and metadata from PDF documents.
"""

from .logic import parse_document, parse_documents_batch
from .pdf_parser import extract_metadata_from_pdf, extract_text_from_pdf, validate_pdf_structure
from .router import router
from .schemas import ParseBatchResponse, ParseRequest, ParseResponse

__all__ = [
    "ParseBatchResponse",
    "ParseRequest",
    "ParseResponse",
    "extract_metadata_from_pdf",
    "extract_text_from_pdf",
    "parse_document",
    "parse_documents_batch",
    "router",
    "validate_pdf_structure",
]
