from __future__ import annotations

import logging
from typing import Any, Callable, Optional

from config import Settings, get_settings
from ocr.async_client import extract_invoice_async
from services.draft_service import DraftService
from services.invoice_service import InvoiceService
from storage.db_async import (
    fetch_invoices_domain_async,
    save_invoice_domain_async,
)
from storage.drafts_async import (
    delete_draft_invoice,
    load_draft_invoice,
    save_draft_invoice,
)


class AppContainer:
    def __init__(
        self,
        config: Optional[Settings] = None,
        ocr_extractor: Optional[Callable[[str, bool, int], Any]] = None,
        save_invoice_func: Optional[Callable[[Any, int], Any]] = None,
        fetch_invoices_func: Optional[Callable[[Optional[Any], Optional[Any], Optional[str]], Any]] = None,
        load_draft_func: Optional[Callable[[int], Any]] = None,
        save_draft_func: Optional[Callable[[int, Any], Any]] = None,
        delete_draft_func: Optional[Callable[[int], Any]] = None,
        invoice_service: Optional[InvoiceService] = None,
        draft_service: Optional[DraftService] = None,
    ) -> None:
        self.config = config or get_settings()

        self._ocr_extractor = ocr_extractor or extract_invoice_async
        self._save_invoice_func = save_invoice_func or save_invoice_domain_async
        self._fetch_invoices_func = fetch_invoices_func or fetch_invoices_domain_async
        self._load_draft_func = load_draft_func or load_draft_invoice
        self._save_draft_func = save_draft_func or save_draft_invoice
        self._delete_draft_func = delete_draft_func or delete_draft_invoice

        self.invoice_service = invoice_service or InvoiceService(
            ocr_extractor=self._ocr_extractor,
            save_invoice_func=self._save_invoice_func,
            fetch_invoices_func=self._fetch_invoices_func,
            logger=logging.getLogger("services.invoice"),
        )

        self.draft_service = draft_service or DraftService(
            load_draft_func=self._load_draft_func,
            save_draft_func=self._save_draft_func,
            delete_draft_func=self._delete_draft_func,
            logger=logging.getLogger("services.draft"),
        )

        # Temporary aliases for backward compatibility with handlers
        self.invoice_service_module = self.invoice_service
        self.draft_service_module = self.draft_service


def create_app_container() -> AppContainer:
    """
    Build the default AppContainer wiring real service and infrastructure modules.
    """
    return AppContainer()


__all__ = ["AppContainer", "create_app_container"]

