"""
Shared module for backend services.
Contains common utilities, database configuration, and shared models.
"""

from .config import ConfigError, Settings, get_config, get_settings, reload_settings
from .exceptions import (
    BaseAppException,
    DocumentNotFoundException,
    ForbiddenException,
    LetterNotFoundException,
    OpenAIException,
    S3DownloadException,
    S3UploadException,
    TemplateNotFoundException,
    UnauthorizedException,
    ValidationException,
    register_exception_handlers,
)
from .schemas import (
    ErrorResponse,
    PaginatedResponse,
    PaginationParams,
    SuccessResponse,
)
from .utils import (
    format_datetime,
    format_file_size,
    generate_uuid,
    parse_file_size,
    sanitize_filename,
    sanitize_html,
)

__all__ = [
    # Exceptions
    "BaseAppException",
    "ConfigError",
    "DocumentNotFoundException",
    "ErrorResponse",
    "ForbiddenException",
    "LetterNotFoundException",
    "OpenAIException",
    "PaginatedResponse",
    "PaginationParams",
    "S3DownloadException",
    "S3UploadException",
    # Config
    "Settings",
    # Schemas
    "SuccessResponse",
    "TemplateNotFoundException",
    "UnauthorizedException",
    "ValidationException",
    "format_datetime",
    "format_file_size",
    # Utils
    "generate_uuid",
    "get_config",
    "get_settings",
    "parse_file_size",
    "register_exception_handlers",
    "reload_settings",
    "sanitize_filename",
    "sanitize_html",
]
