"""
Typed dependency accessors for handlers.

Provides type-safe functions to extract services from the AppContainer
injected by ContainerMiddleware.
"""

from __future__ import annotations

from typing import Any, Dict

from core.container import AppContainer
from services.draft_service import DraftService
from services.invoice_service import InvoiceService


def get_container(data: Dict[str, Any]) -> AppContainer:
    """
    Extract AppContainer from aiogram handler data.

    Raises AssertionError if container is not present or has wrong type.
    """
    container = data["container"]
    assert isinstance(container, AppContainer)
    return container


def get_invoice_service(container: AppContainer) -> InvoiceService:
    """Extract InvoiceService from AppContainer."""
    return container.invoice_service


def get_draft_service(container: AppContainer) -> DraftService:
    """Extract DraftService from AppContainer."""
    return container.draft_service


__all__ = [
    "get_container",
    "get_invoice_service",
    "get_draft_service",
]
