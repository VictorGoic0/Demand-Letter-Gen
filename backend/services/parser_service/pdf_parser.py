"""
PDF parser implementation using pypdf library.
Handles text extraction and metadata extraction from PDF files.
"""
import logging
import io
from typing import Dict, Any, Optional
from pypdf import PdfReader
from pypdf.errors import PdfReadError, PdfStreamError

logger = logging.getLogger(__name__)


def validate_pdf_structure(file_content: bytes) -> bool:
    """
    Validate that the file content is a valid PDF structure.
    
    Args:
        file_content: PDF file content as bytes
        
    Returns:
        True if PDF structure is valid, False otherwise
    """
    try:
        # Check PDF header (should start with %PDF-)
        if not file_content.startswith(b"%PDF-"):
            logger.warning("File does not start with PDF header")
            return False
        
        # Try to create a reader to validate structure
        file_obj = io.BytesIO(file_content)
        reader = PdfReader(file_obj)
        
        # Check if PDF has at least one page
        if len(reader.pages) == 0:
            logger.warning("PDF has no pages")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"PDF structure validation failed: {str(e)}")
        return False


def extract_text_from_pdf(
    file_content: bytes,
    page_separator: str = "\n\n--- Page {page_num} ---\n\n",
) -> str:
    """
    Extract text from a PDF file.
    
    Args:
        file_content: PDF file content as bytes
        page_separator: String to separate pages in output (default: "\n\n--- Page {page_num} ---\n\n")
        
    Returns:
        Extracted text from all pages, concatenated with separators
        
    Raises:
        PdfReadError: If PDF is corrupted or cannot be read
        PdfStreamError: If PDF stream is invalid
        ValueError: If PDF structure is invalid
    """
    try:
        # Validate PDF structure first
        if not validate_pdf_structure(file_content):
            raise ValueError("Invalid PDF structure")
        
        # Create file-like object from bytes
        file_obj = io.BytesIO(file_content)
        
        # Create PDF reader
        reader = PdfReader(file_obj)
        
        # Check if PDF is encrypted
        if reader.is_encrypted:
            logger.warning("PDF is encrypted, attempting to decrypt with empty password")
            # Try to decrypt with empty password (common for some PDFs)
            if not reader.decrypt(""):
                raise ValueError("PDF is encrypted and cannot be decrypted with empty password")
        
        # Extract text from all pages
        extracted_text_parts = []
        total_pages = len(reader.pages)
        
        for page_num, page in enumerate(reader.pages, start=1):
            try:
                page_text = page.extract_text()
                
                # Add page separator if specified
                if page_separator and total_pages > 1:
                    separator = page_separator.format(page_num=page_num)
                    extracted_text_parts.append(separator)
                
                extracted_text_parts.append(page_text)
                
            except Exception as e:
                logger.warning(f"Failed to extract text from page {page_num}: {str(e)}")
                # Continue with other pages even if one fails
                if page_separator and total_pages > 1:
                    separator = page_separator.format(page_num=page_num)
                    extracted_text_parts.append(separator)
                extracted_text_parts.append(f"[Error extracting text from page {page_num}]")
        
        # Concatenate all pages
        extracted_text = "".join(extracted_text_parts)
        
        logger.info(f"Extracted text from {total_pages} pages")
        return extracted_text
        
    except PdfReadError as e:
        logger.error(f"PDF read error: {str(e)}")
        raise ValueError(f"Failed to read PDF: {str(e)}") from e
    except PdfStreamError as e:
        logger.error(f"PDF stream error: {str(e)}")
        raise ValueError(f"Invalid PDF stream: {str(e)}") from e
    except Exception as e:
        logger.error(f"Unexpected error extracting text from PDF: {str(e)}")
        raise ValueError(f"Failed to extract text from PDF: {str(e)}") from e


def extract_metadata_from_pdf(file_content: bytes) -> Dict[str, Any]:
    """
    Extract metadata from a PDF file.
    
    Args:
        file_content: PDF file content as bytes
        
    Returns:
        Dictionary containing:
            - page_count: Number of pages
            - file_size: File size in bytes
            - creation_date: Creation date if available (ISO format string or None)
            - modification_date: Modification date if available (ISO format string or None)
            - title: Document title if available
            - author: Document author if available
            - subject: Document subject if available
            - creator: PDF creator if available
            - producer: PDF producer if available
            
    Raises:
        ValueError: If PDF structure is invalid
    """
    try:
        # Validate PDF structure first
        if not validate_pdf_structure(file_content):
            raise ValueError("Invalid PDF structure")
        
        # Create file-like object from bytes
        file_obj = io.BytesIO(file_content)
        
        # Create PDF reader
        reader = PdfReader(file_obj)
        
        # Get file size
        file_size = len(file_content)
        
        # Get page count
        page_count = len(reader.pages)
        
        # Extract metadata
        metadata = reader.metadata
        
        # Build result dictionary
        result = {
            "page_count": page_count,
            "file_size": file_size,
            "creation_date": None,
            "modification_date": None,
            "title": None,
            "author": None,
            "subject": None,
            "creator": None,
            "producer": None,
        }
        
        # Extract metadata fields if available
        if metadata:
            # Convert dates to ISO format strings if available
            if hasattr(metadata, "creation_date") and metadata.creation_date:
                try:
                    result["creation_date"] = metadata.creation_date.isoformat()
                except Exception:
                    result["creation_date"] = str(metadata.creation_date)
            
            if hasattr(metadata, "modification_date") and metadata.modification_date:
                try:
                    result["modification_date"] = metadata.modification_date.isoformat()
                except Exception:
                    result["modification_date"] = str(metadata.modification_date)
            
            # Extract text fields
            if hasattr(metadata, "title") and metadata.title:
                result["title"] = str(metadata.title)
            
            if hasattr(metadata, "author") and metadata.author:
                result["author"] = str(metadata.author)
            
            if hasattr(metadata, "subject") and metadata.subject:
                result["subject"] = str(metadata.subject)
            
            if hasattr(metadata, "creator") and metadata.creator:
                result["creator"] = str(metadata.creator)
            
            if hasattr(metadata, "producer") and metadata.producer:
                result["producer"] = str(metadata.producer)
        
        logger.info(f"Extracted metadata: {page_count} pages, {file_size} bytes")
        return result
        
    except Exception as e:
        logger.error(f"Error extracting metadata from PDF: {str(e)}")
        raise ValueError(f"Failed to extract metadata from PDF: {str(e)}") from e

