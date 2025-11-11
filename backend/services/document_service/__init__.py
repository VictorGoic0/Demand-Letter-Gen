"""
Document service for managing uploaded documents.
"""
from .router import router
from .handler import (
    upload_handler,
    list_handler,
    get_handler,
    delete_handler,
    download_handler,
)

__all__ = [
    "router",
    "upload_handler",
    "list_handler",
    "get_handler",
    "delete_handler",
    "download_handler",
]

