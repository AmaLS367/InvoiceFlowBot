from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class AppContainer:
    """
    Simple application-wide dependency container.

    For now it stores references to modules that implement
    services and infrastructure. In later stages we can replace
    these modules with test doubles or alternative implementations.
    """

    invoice_service_module: Any
    draft_service_module: Any
    db_async_module: Any
    ocr_async_client_module: Any


def create_app_container() -> AppContainer:
    """
    Build the default AppContainer for the application.

    This function wires together the current production implementations
    of services and infrastructure.
    """
    from ocr import async_client
    from services import draft_service, invoice_service
    from storage import db_async

    return AppContainer(
        invoice_service_module=invoice_service,
        draft_service_module=draft_service,
        db_async_module=db_async,
        ocr_async_client_module=async_client,
    )


__all__ = ["AppContainer", "create_app_container"]

