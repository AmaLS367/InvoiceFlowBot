from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any, Dict, List

from domain.invoices import (
    Invoice,
    InvoiceHeader,
    InvoiceItem,
    InvoiceSourceInfo,
)


def invoice_to_db_row(invoice: Invoice, user_id: int = 0) -> Dict[str, Any]:
    header = invoice.header
    date_iso = None
    if header.invoice_date:
        date_iso = header.invoice_date.isoformat()

    source_path = None
    if invoice.source and invoice.source.file_path:
        source_path = invoice.source.file_path

    total_sum = None
    if header.total_amount is not None:
        total_sum = float(header.total_amount)

    return {
        "user_id": user_id,
        "supplier": header.supplier_name,
        "client": header.customer_name,
        "doc_number": header.invoice_number,
        "date": header.invoice_date.isoformat() if header.invoice_date else None,
        "date_iso": date_iso,
        "total_sum": total_sum,
        "raw_text": "",
        "source_path": source_path or "",
    }


def invoice_item_to_db_row(invoice_id: int, item: InvoiceItem, index: int) -> Dict[str, Any]:
    return {
        "invoice_id": invoice_id,
        "idx": index,
        "code": item.sku or "",
        "name": item.description or "",
        "qty": float(item.quantity),
        "price": float(item.unit_price),
        "total": float(item.line_total),
    }


def db_row_to_invoice_item(row: Dict[str, Any]) -> InvoiceItem:
    return InvoiceItem(
        description=row.get("name") or "",
        sku=row.get("code"),
        quantity=Decimal(str(row.get("qty", 0))),
        unit_price=Decimal(str(row.get("price", 0))),
        line_total=Decimal(str(row.get("total", 0))),
    )


def db_row_to_invoice(header_row: Dict[str, Any], item_rows: List[Dict[str, Any]]) -> Invoice:
    invoice_date = None
    if header_row.get("date_iso"):
        try:
            invoice_date = date.fromisoformat(header_row["date_iso"])
        except (ValueError, TypeError):
            pass

    total_amount = None
    if header_row.get("total_sum") is not None:
        total_amount = Decimal(str(header_row["total_sum"]))

    header = InvoiceHeader(
        supplier_name=header_row.get("supplier"),
        customer_name=header_row.get("client"),
        invoice_number=header_row.get("doc_number"),
        invoice_date=invoice_date,
        total_amount=total_amount,
    )

    items: List[InvoiceItem] = [db_row_to_invoice_item(item_row) for item_row in item_rows]

    source = InvoiceSourceInfo(
        file_path=header_row.get("source_path"),
        file_sha256=None,
        provider=None,
        raw_payload_path=None,
    )

    invoice = Invoice(
        header=header,
        items=items,
        comments=[],
        source=source,
    )

    return invoice


__all__ = [
    "invoice_to_db_row",
    "invoice_item_to_db_row",
    "db_row_to_invoice_item",
    "db_row_to_invoice",
]
