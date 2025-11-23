"""
High-level business logic for invoice processing.

Coordinates OCR results, domain models and persistence layer.
"""
from __future__ import annotations

import logging
from datetime import date, datetime
from decimal import Decimal
from typing import Awaitable, Callable, List, Optional

from domain.invoices import (
    Invoice,
    InvoiceHeader,
    InvoiceItem,
    InvoiceSourceInfo,
)
from ocr.engine.types import ExtractionResult, Item


def _parse_date(value: Optional[str]) -> Optional[date]:
    """
    Best-effort parse for invoice dates coming from OCR.
    Returns None if parsing fails.
    """
    if not value:
        return None

    formats = [
        "%Y-%m-%d",
        "%d.%m.%Y",
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(value, fmt)
            return dt.date()
        except (ValueError, TypeError):
            continue

    return None


def _build_header(result: ExtractionResult) -> InvoiceHeader:
    """
    Build InvoiceHeader from OCR ExtractionResult.
    """
    invoice_date = _parse_date(result.date)

    total_amount = None
    if result.total_sum is not None:
        total_amount = Decimal(str(result.total_sum))

    return InvoiceHeader(
        supplier_name=result.supplier,
        customer_name=result.client,
        invoice_date=invoice_date,
        total_amount=total_amount,
    )


def _build_item(item: Item) -> InvoiceItem:
    """
    Build a single InvoiceItem from OCR Item.
    """
    return InvoiceItem(
        description=item.name,
        sku=item.code,
        quantity=Decimal(str(item.qty)),
        unit_price=Decimal(str(item.price)),
        line_total=Decimal(str(item.total)),
    )


def _build_source_info(result: ExtractionResult, provider: str = "mindee") -> InvoiceSourceInfo:
    """
    Build InvoiceSourceInfo from ExtractionResult and provider name.
    """
    return InvoiceSourceInfo(
        provider=provider,
    )


def build_invoice_from_extraction(result: ExtractionResult) -> Invoice:
    """
    Convert OCR ExtractionResult into a domain Invoice entity.
    """
    header = _build_header(result)
    items = [_build_item(it) for it in result.items]
    source = _build_source_info(result, provider="mindee")

    invoice = Invoice(
        header=header,
        items=items,
        comments=[],
        source=source,
    )

    return invoice


class InvoiceService:
    def __init__(
        self,
        ocr_extractor: Callable[[str, bool, int], Awaitable[ExtractionResult]],
        save_invoice_func: Callable[[Invoice, int], Awaitable[int]],
        fetch_invoices_func: Callable[[Optional[date], Optional[date], Optional[str]], Awaitable[List[Invoice]]],
        logger: logging.Logger,
    ) -> None:
        self._ocr_extractor = ocr_extractor
        self._save_invoice_func = save_invoice_func
        self._fetch_invoices_func = fetch_invoices_func
        self._logger = logger


    async def process_invoice_file(
        self,
        pdf_path: str,
        fast: bool = True,
        max_pages: int = 12,
    ) -> Invoice:
        """
        Run OCR on the given file and map the result into an Invoice domain object.
        """
        self._logger.info(
            f"[SERVICE] process_invoice_file start path={pdf_path} fast={fast} max_pages={max_pages}"
        )

        result = await self._ocr_extractor(
            pdf_path,
            fast,
            max_pages,
        )
        invoice = build_invoice_from_extraction(result)

        self._logger.info(
            f"[SERVICE] process_invoice_file done path={pdf_path} items={len(invoice.items)}"
        )

        return invoice

    async def save_invoice(self, invoice: Invoice, user_id: int = 0) -> int:
        """
        Persist an Invoice to the database and return its ID.
        """
        self._logger.info(
            f"[SERVICE] save_invoice supplier={invoice.header.supplier_name!r} total={invoice.header.total_amount!r}"
        )

        invoice_id = await self._save_invoice_func(
            invoice,
            user_id,
        )

        return invoice_id

    async def list_invoices(
        self,
        from_date: Optional[date],
        to_date: Optional[date],
        supplier: Optional[str] = None,
    ) -> List[Invoice]:
        """
        Fetch invoices for the given date period, sorted by creation time.

        Optionally filter by supplier name.
        """
        self._logger.info(
            f"[SERVICE] list_invoices from={from_date} to={to_date} supplier={supplier!r}"
        )

        invoices = await self._fetch_invoices_func(
            from_date,
            to_date,
            supplier,
        )

        return invoices


__all__ = [
    "InvoiceService",
    "build_invoice_from_extraction",
]

