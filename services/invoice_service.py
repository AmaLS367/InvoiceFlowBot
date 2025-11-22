"""
High-level business logic for invoice processing.

Coordinates OCR results, domain models and persistence layer.
"""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from domain.invoices import (
    Invoice,
    InvoiceHeader,
    InvoiceItem,
    InvoiceSourceInfo,
)
from ocr.async_client import extract_invoice_async
from ocr.engine.types import ExtractionResult, Item
from ocr.engine.util import get_logger
from storage import db as storage_db  # noqa: F401
from storage.db_async import (
    fetch_invoices_domain_async,
    save_invoice_domain_async,
)

logger = get_logger("services.invoice")


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


async def process_invoice_file(
    pdf_path: str,
    fast: bool = True,
    max_pages: int = 12,
) -> Invoice:
    """
    Run OCR on the given file and map the result into an Invoice domain object.
    """
    logger.info(
        f"[SERVICE] process_invoice_file start path={pdf_path} fast={fast} max_pages={max_pages}"
    )

    result = await extract_invoice_async(
        pdf_path=pdf_path,
        fast=fast,
        max_pages=max_pages,
    )
    invoice = build_invoice_from_extraction(result)

    logger.info(
        f"[SERVICE] process_invoice_file done path={pdf_path} items={len(invoice.items)}"
    )

    return invoice


async def save_invoice(invoice: Invoice, user_id: int = 0) -> int:
    """
    Persist an Invoice to the database and return its ID.
    """
    logger.info(
        f"[SERVICE] save_invoice supplier={invoice.header.supplier_name!r} total={invoice.header.total_amount!r}"
    )

    invoice_id = await save_invoice_domain_async(
        invoice=invoice,
        user_id=user_id,
    )

    return invoice_id


async def list_invoices(
    from_date: Optional[date],
    to_date: Optional[date],
    supplier: Optional[str] = None,
) -> List[Invoice]:
    """
    Fetch invoices for the given date period, sorted by creation time.

    Optionally filter by supplier name.
    """
    logger.info(
        f"[SERVICE] list_invoices from={from_date} to={to_date} supplier={supplier!r}"
    )

    invoices = await fetch_invoices_domain_async(
        from_date=from_date,
        to_date=to_date,
        supplier=supplier,
    )

    return invoices


__all__ = [
    "build_invoice_from_extraction",
    "process_invoice_file",
    "save_invoice",
    "list_invoices",
]

