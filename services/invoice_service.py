"""
Service layer for invoice processing: OCR pipeline integration and domain model conversion.
"""
from __future__ import annotations

from datetime import datetime, date
from decimal import Decimal
from typing import Optional

from ocr.engine.types import ExtractionResult, Item
from ocr.engine.router import extract_invoice
from ocr.engine.util import get_logger
from domain.invoices import (
    Invoice,
    InvoiceHeader,
    InvoiceItem,
    InvoiceSourceInfo,
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


def process_invoice_file(pdf_path: str, fast: bool = True, max_pages: int = 12) -> Invoice:
    """
    Run the OCR pipeline for a single PDF/image and return a domain Invoice.
    """
    logger.info(
        f"[SERVICE] process_invoice_file start path={pdf_path} fast={fast} max_pages={max_pages}"
    )

    result = extract_invoice(pdf_path=pdf_path, fast=fast, max_pages=max_pages)
    invoice = build_invoice_from_extraction(result)

    logger.info(
        f"[SERVICE] process_invoice_file done path={pdf_path} items={len(invoice.items)}"
    )

    return invoice


__all__ = [
    "build_invoice_from_extraction",
    "process_invoice_file",
]

