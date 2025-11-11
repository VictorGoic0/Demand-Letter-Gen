"""
Shared module for backend services.
Contains common utilities, database configuration, and shared models.
"""
from .config import Settings, get_settings, get_config, reload_settings, ConfigError
from .exceptions import (
    BaseAppException,
    DocumentNotFoundException,
    TemplateNotFoundException,
    LetterNotFoundException,
    S3UploadException,
    S3DownloadException,
    OpenAIException,
    ValidationException,
    UnauthorizedException,
    ForbiddenException,
    register_exception_handlers,
)
from .utils import (
    generate_uuid,
    format_datetime,
    format_file_size,
    sanitize_filename,
    sanitize_html,
    parse_file_size,
)
from .schemas import (
    SuccessResponse,
    ErrorResponse,
    PaginationParams,
    PaginatedResponse,
)

__all__ = [
    # Config
    "Settings",
    "get_settings",
    "get_config",
    "reload_settings",
    "ConfigError",
    # Exceptions
    "BaseAppException",
    "DocumentNotFoundException",
    "TemplateNotFoundException",
    "LetterNotFoundException",
    "S3UploadException",
    "S3DownloadException",
    "OpenAIException",
    "ValidationException",
    "UnauthorizedException",
    "ForbiddenException",
    "register_exception_handlers",
    # Utils
    "generate_uuid",
    "format_datetime",
    "format_file_size",
    "sanitize_filename",
    "sanitize_html",
    "parse_file_size",
    # Schemas
    "SuccessResponse",
    "ErrorResponse",
    "PaginationParams",
    "PaginatedResponse",
]

