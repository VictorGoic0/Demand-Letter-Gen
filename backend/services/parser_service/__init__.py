"""
Parser service for extracting text and metadata from PDF documents.
"""
from .pdf_parser import extract_text_from_pdf, extract_metadata_from_pdf, validate_pdf_structure
from .schemas import ParseRequest, ParseResponse, ParseBatchResponse
from .logic import parse_document, parse_documents_batch
from .router import router

__all__ = [
    "extract_text_from_pdf",
    "extract_metadata_from_pdf",
    "validate_pdf_structure",
    "ParseRequest",
    "ParseResponse",
    "ParseBatchResponse",
    "parse_document",
    "parse_documents_batch",
    "router",
]

