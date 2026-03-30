"""
Template service for managing letter templates.
"""

from .handler import (
    create_handler_func,
    delete_handler_func,
    get_default_handler_func,
    get_handler_func,
    list_handler_func,
    update_handler_func,
)
from .router import router

__all__ = [
    "create_handler_func",
    "delete_handler_func",
    "get_default_handler_func",
    "get_handler_func",
    "list_handler_func",
    "router",
    "update_handler_func",
]
