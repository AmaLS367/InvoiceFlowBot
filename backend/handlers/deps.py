from __future__ import annotations

from typing import Any, Dict

from backend.core.container import AppContainer
from backend.services.draft_service import DraftService
from backend.services.invoice_service import InvoiceService


def get_container(data: Dict[str, Any]) -> AppContainer:
    container = data["container"]
    assert isinstance(container, AppContainer)
    return container


def get_invoice_service(container: AppContainer) -> InvoiceService:
    return container.invoice_service


def get_draft_service(container: AppContainer) -> DraftService:
    return container.draft_service


__all__ = [
    "get_container",
    "get_invoice_service",
    "get_draft_service",
]
