from __future__ import annotations

from datetime import date
from decimal import Decimal

from domain.invoices import Invoice, InvoiceHeader, InvoiceItem
from storage.mappers import (
    db_row_to_invoice,
    invoice_item_to_db_row,
    invoice_to_db_row,
)


def test_invoice_to_db_row():
    """Test invoice_to_db_row function."""
    header = InvoiceHeader(
        supplier_name="Test Supplier",
        customer_name="Test Customer",
        invoice_number="INV-001",
        invoice_date=date(2025, 1, 15),
        total_amount=Decimal("100.00"),
    )
    items = [
        InvoiceItem(
            description="Item 1",
            sku="SKU-001",
            quantity=Decimal("2"),
            unit_price=Decimal("25.00"),
            line_total=Decimal("50.00"),
        ),
    ]
    invoice = Invoice(header=header, items=items)

    row = invoice_to_db_row(invoice, user_id=123)

    assert row["user_id"] == 123
    assert row["supplier"] == "Test Supplier"
    assert row["client"] == "Test Customer"
    assert row["doc_number"] == "INV-001"
    assert row["date"] == "2025-01-15"
    assert row["total_sum"] == 100.0


def test_invoice_item_to_db_row():
    """Test invoice_item_to_db_row function."""
    item = InvoiceItem(
        description="Test Item",
        sku="SKU-001",
        quantity=Decimal("2"),
        unit_price=Decimal("25.00"),
        line_total=Decimal("50.00"),
    )

    row = invoice_item_to_db_row(invoice_id=1, item=item, index=1)

    assert row["invoice_id"] == 1
    assert row["idx"] == 1
    assert row["name"] == "Test Item"
    assert row["code"] == "SKU-001"
    assert row["qty"] == 2.0
    assert row["price"] == 25.0
    assert row["total"] == 50.0


def test_db_row_to_invoice():
    """Test db_row_to_invoice function."""

    header_row = {
        "id": 1,
        "user_id": 123,
        "supplier": "Test Supplier",
        "client": "Test Customer",
        "doc_number": "INV-001",
        "date_iso": "2025-01-15",
        "total_sum": 100.0,
        "source_path": "test.pdf",
    }

    item_rows = [
        {
            "code": "SKU-001",
            "name": "Item 1",
            "qty": 2.0,
            "price": 25.0,
            "total": 50.0,
        },
    ]

    invoice = db_row_to_invoice(header_row, item_rows)

    assert invoice.header.supplier_name == "Test Supplier"
    assert invoice.header.customer_name == "Test Customer"
    assert invoice.header.invoice_number == "INV-001"
    assert invoice.header.invoice_date == date(2025, 1, 15)
    assert invoice.header.total_amount == Decimal("100.0")
    assert len(invoice.items) == 1
    assert invoice.items[0].description == "Item 1"


def test_db_row_to_invoice_with_none_values():
    """Test db_row_to_invoice with None values."""
    header_row = {
        "id": 1,
        "user_id": 123,
        "supplier": None,
        "client": None,
        "doc_number": None,
        "date_iso": None,
        "total_sum": None,
        "source_path": None,
    }

    invoice = db_row_to_invoice(header_row, item_rows=[])

    assert invoice.header.supplier_name is None
    assert invoice.header.customer_name is None
    assert invoice.header.invoice_number is None
    assert invoice.header.invoice_date is None
    assert invoice.header.total_amount is None
    assert len(invoice.items) == 0


def test_db_row_to_invoice_item():
    """Test db_row_to_invoice_item function."""
    from storage.mappers import db_row_to_invoice_item

    row = {
        "code": "SKU-001",
        "name": "Test Item",
        "qty": 2.0,
        "price": 25.0,
        "total": 50.0,
    }

    item = db_row_to_invoice_item(row)

    assert item.description == "Test Item"
    assert item.sku == "SKU-001"
    assert item.quantity == Decimal("2.0")
    assert item.unit_price == Decimal("25.0")
    assert item.line_total == Decimal("50.0")
