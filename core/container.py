from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class AppContainer:
    """
    Simple dependency container holding references to service and infrastructure modules.
    """

    invoice_service_module: Any
    draft_service_module: Any
    db_async_module: Any
    ocr_async_client_module: Any


def create_app_container() -> AppContainer:
    """
    Build the default AppContainer wiring real service and infrastructure modules.
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

