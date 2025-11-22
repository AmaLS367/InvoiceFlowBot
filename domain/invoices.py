"""
Domain models and value objects describing invoices and their items.
"""
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional


@dataclass
class InvoiceItem:
    """
    Single line item in an invoice.
    """
    description: str
    sku: Optional[str] = None
    quantity: Decimal = Decimal("0")
    unit_price: Decimal = Decimal("0")
    line_total: Decimal = Decimal("0")
    currency: Optional[str] = None


@dataclass
class InvoiceHeader:
    """
    Invoice header information: supplier, customer, dates, totals.
    """
    supplier_name: Optional[str] = None
    supplier_tax_id: Optional[str] = None
    customer_name: Optional[str] = None
    customer_tax_id: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[date] = None
    due_date: Optional[date] = None
    currency: Optional[str] = None
    subtotal: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None
    total_amount: Optional[Decimal] = None


@dataclass
class InvoiceComment:
    """
    Comment attached to an invoice.
    """
    message: str
    author: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class InvoiceSourceInfo:
    """
    Source metadata for invoice data: OCR provider, file paths.
    """
    file_path: Optional[str] = None
    file_sha256: Optional[str] = None
    provider: Optional[str] = None
    raw_payload_path: Optional[str] = None


@dataclass
class Invoice:
    """
    Canonical invoice representation used across the application.
    """
    header: InvoiceHeader
    items: List[InvoiceItem] = field(default_factory=list)
    comments: List[InvoiceComment] = field(default_factory=list)
    source: Optional[InvoiceSourceInfo] = None

    def total_items(self) -> int:
        return len(self.items)

    def has_items(self) -> bool:
        return len(self.items) > 0


__all__ = [
    "InvoiceHeader",
    "InvoiceItem",
    "InvoiceComment",
    "InvoiceSourceInfo",
    "Invoice",
]

