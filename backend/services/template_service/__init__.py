"""
Template service for managing letter templates.
"""
from .router import router
from .handler import (
    create_handler_func,
    list_handler_func,
    get_default_handler_func,
    get_handler_func,
    update_handler_func,
    delete_handler_func,
)

__all__ = [
    "router",
    "create_handler_func",
    "list_handler_func",
    "get_default_handler_func",
    "get_handler_func",
    "update_handler_func",
    "delete_handler_func",
]

