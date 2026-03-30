"""
Document service for managing uploaded documents.
"""

from .handler import (
    delete_handler,
    download_handler,
    get_handler,
    list_handler,
    upload_handler,
)
from .router import router

__all__ = [
    "delete_handler",
    "download_handler",
    "get_handler",
    "list_handler",
    "router",
    "upload_handler",
]
