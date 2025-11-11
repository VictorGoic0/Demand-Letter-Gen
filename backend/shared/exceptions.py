"""
Custom exception classes and exception handlers for FastAPI.
"""
from typing import Optional
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from .schemas import ErrorResponse


class BaseAppException(Exception):
    """Base exception class for application exceptions."""
    def __init__(
        self,
        message: str,
        detail: Optional[str] = None,
        code: Optional[str] = None,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    ):
        self.message = message
        self.detail = detail
        self.code = code or self.__class__.__name__
        self.status_code = status_code
        super().__init__(self.message)


class DocumentNotFoundException(BaseAppException):
    """Raised when a document is not found."""
    def __init__(self, document_id: Optional[str] = None, detail: Optional[str] = None):
        message = f"Document not found"
        if document_id:
            message = f"Document with ID '{document_id}' not found"
        super().__init__(
            message=message,
            detail=detail or "The requested document does not exist",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class TemplateNotFoundException(BaseAppException):
    """Raised when a template is not found."""
    def __init__(self, template_id: Optional[str] = None, detail: Optional[str] = None):
        message = f"Template not found"
        if template_id:
            message = f"Template with ID '{template_id}' not found"
        super().__init__(
            message=message,
            detail=detail or "The requested template does not exist",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class LetterNotFoundException(BaseAppException):
    """Raised when a letter is not found."""
    def __init__(self, letter_id: Optional[str] = None, detail: Optional[str] = None):
        message = f"Letter not found"
        if letter_id:
            message = f"Letter with ID '{letter_id}' not found"
        super().__init__(
            message=message,
            detail=detail or "The requested letter does not exist",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class S3UploadException(BaseAppException):
    """Raised when an S3 upload operation fails."""
    def __init__(self, message: str = "S3 upload failed", detail: Optional[str] = None):
        super().__init__(
            message=message,
            detail=detail or "Failed to upload file to S3",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class S3DownloadException(BaseAppException):
    """Raised when an S3 download operation fails."""
    def __init__(self, message: str = "S3 download failed", detail: Optional[str] = None):
        super().__init__(
            message=message,
            detail=detail or "Failed to download file from S3",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class OpenAIException(BaseAppException):
    """Raised when an OpenAI API operation fails."""
    def __init__(self, message: str = "OpenAI API error", detail: Optional[str] = None):
        super().__init__(
            message=message,
            detail=detail or "Failed to communicate with OpenAI API",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class ValidationException(BaseAppException):
    """Raised when validation fails."""
    def __init__(self, message: str = "Validation failed", detail: Optional[str] = None):
        super().__init__(
            message=message,
            detail=detail or "The provided data is invalid",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


class UnauthorizedException(BaseAppException):
    """Raised when authentication is required or fails."""
    def __init__(self, message: str = "Unauthorized", detail: Optional[str] = None):
        super().__init__(
            message=message,
            detail=detail or "Authentication required",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class ForbiddenException(BaseAppException):
    """Raised when access is forbidden."""
    def __init__(self, message: str = "Forbidden", detail: Optional[str] = None):
        super().__init__(
            message=message,
            detail=detail or "You do not have permission to access this resource",
            status_code=status.HTTP_403_FORBIDDEN,
        )


async def app_exception_handler(request: Request, exc: BaseAppException) -> JSONResponse:
    """
    Handler for custom application exceptions.
    
    Args:
        request: FastAPI request object
        exc: Application exception instance
        
    Returns:
        JSONResponse with error details
    """
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            success=False,
            error=exc.message,
            detail=exc.detail,
            code=exc.code,
        ).dict(),
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    Handler for HTTP exceptions.
    
    Args:
        request: FastAPI request object
        exc: HTTP exception instance
        
    Returns:
        JSONResponse with error details
    """
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            success=False,
            error=exc.detail,
            detail=None,
            code=f"HTTP_{exc.status_code}",
        ).dict(),
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handler for request validation errors.
    
    Args:
        request: FastAPI request object
        exc: Validation exception instance
        
    Returns:
        JSONResponse with validation error details
    """
    errors = exc.errors()
    error_messages = []
    for error in errors:
        field = ".".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        error_messages.append(f"{field}: {message}")
    
    detail = "; ".join(error_messages)
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            success=False,
            error="Validation error",
            detail=detail,
            code="VALIDATION_ERROR",
        ).dict(),
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handler for unhandled exceptions.
    
    Args:
        request: FastAPI request object
        exc: Exception instance
        
    Returns:
        JSONResponse with error details
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.exception(f"Unhandled exception: {exc}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            success=False,
            error="Internal server error",
            detail="An unexpected error occurred",
            code="INTERNAL_SERVER_ERROR",
        ).dict(),
    )


def register_exception_handlers(app):
    """
    Register all exception handlers with a FastAPI app.
    
    Args:
        app: FastAPI application instance
    """
    # Register custom application exceptions
    app.add_exception_handler(BaseAppException, app_exception_handler)
    
    # Register HTTP exceptions
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    
    # Register validation exceptions
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    
    # Register general exception handler (should be last)
    app.add_exception_handler(Exception, general_exception_handler)

