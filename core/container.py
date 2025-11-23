from __future__ import annotations

import logging
from datetime import date
from typing import Awaitable, Callable, List, Optional

from config import Settings, get_settings
from domain.drafts import InvoiceDraft
from domain.invoices import Invoice
from ocr.async_client import extract_invoice_async
from ocr.engine.types import ExtractionResult
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
        ocr_extractor: Optional[Callable[[str, bool, int], Awaitable[ExtractionResult]]] = None,
        save_invoice_func: Optional[Callable[[Invoice, int], Awaitable[int]]] = None,
        fetch_invoices_func: Optional[Callable[[Optional[date], Optional[date], Optional[str]], Awaitable[List[Invoice]]]] = None,
        load_draft_func: Optional[Callable[[int], Awaitable[Optional[InvoiceDraft]]]] = None,
        save_draft_func: Optional[Callable[[int, InvoiceDraft], Awaitable[None]]] = None,
        delete_draft_func: Optional[Callable[[int], Awaitable[None]]] = None,
        invoice_service: Optional[InvoiceService] = None,
        draft_service: Optional[DraftService] = None,
    ) -> None:
        self.config: Settings = config or get_settings()

        self._ocr_extractor: Callable[[str, bool, int], Awaitable[ExtractionResult]] = ocr_extractor or extract_invoice_async
        self._save_invoice_func: Callable[[Invoice, int], Awaitable[int]] = save_invoice_func or save_invoice_domain_async
        self._fetch_invoices_func: Callable[[Optional[date], Optional[date], Optional[str]], Awaitable[List[Invoice]]] = fetch_invoices_func or fetch_invoices_domain_async
        self._load_draft_func: Callable[[int], Awaitable[Optional[InvoiceDraft]]] = load_draft_func or load_draft_invoice
        self._save_draft_func: Callable[[int, InvoiceDraft], Awaitable[None]] = save_draft_func or save_draft_invoice
        self._delete_draft_func: Callable[[int], Awaitable[None]] = delete_draft_func or delete_draft_invoice

        self.invoice_service: InvoiceService = invoice_service or InvoiceService(
            ocr_extractor=self._ocr_extractor,
            save_invoice_func=self._save_invoice_func,
            fetch_invoices_func=self._fetch_invoices_func,
            logger=logging.getLogger("services.invoice"),
        )

        self.draft_service: DraftService = draft_service or DraftService(
            load_draft_func=self._load_draft_func,
            save_draft_func=self._save_draft_func,
            delete_draft_func=self._delete_draft_func,
            logger=logging.getLogger("services.draft"),
        )

        # Temporary aliases for backward compatibility with handlers
        self.invoice_service_module: InvoiceService = self.invoice_service
        self.draft_service_module: DraftService = self.draft_service


def create_app_container() -> AppContainer:
    """
    Build the default AppContainer wiring real service and infrastructure modules.
    """
    return AppContainer()


__all__ = ["AppContainer", "create_app_container"]

