"""
Integration tests for AsyncInvoiceStorage with Alembic migrations.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from domain.invoices import Invoice, InvoiceHeader, InvoiceItem, InvoiceSourceInfo
from storage.db_async import AsyncInvoiceStorage

pytestmark = pytest.mark.storage_db


@pytest.mark.asyncio
async def test_async_storage_works_with_migrated_schema(
    async_storage_with_migrations: AsyncInvoiceStorage,
) -> None:
    """
    Test that AsyncInvoiceStorage can save and fetch invoices from a migrated database.

    This test verifies:
    - Alembic migrations run successfully
    - Storage can write invoices to the database
    - Storage can read invoices from the database
    """
    storage = async_storage_with_migrations

    # Create a test invoice
    header = InvoiceHeader(
        supplier_name="Test Supplier",
        customer_name="Test Customer",
        invoice_number="INV-001",
        invoice_date=date(2025, 1, 1),
        total_amount=Decimal("1000.00"),
    )

    items = [
        InvoiceItem(
            description="Test Item 1",
            sku="SKU-001",
            quantity=Decimal("2.0"),
            unit_price=Decimal("500.00"),
            line_total=Decimal("1000.00"),
        )
    ]

    source = InvoiceSourceInfo(
        file_path="test/invoice.pdf",
        provider="test",
    )

    invoice = Invoice(
        header=header,
        items=items,
        comments=[],
        source=source,
    )

    # Save invoice
    invoice_id = await storage.save_invoice(invoice, user_id=123)

    assert invoice_id > 0

    # Fetch invoices
    from_date = date(2024, 12, 31)
    to_date = date(2025, 1, 2)

    fetched_invoices = await storage.fetch_invoices(
        from_date=from_date,
        to_date=to_date,
        supplier=None,
    )

    assert len(fetched_invoices) == 1
    fetched = fetched_invoices[0]

    # Verify invoice data
    assert fetched.header.supplier_name == invoice.header.supplier_name
    assert fetched.header.customer_name == invoice.header.customer_name
    assert fetched.header.invoice_number == invoice.header.invoice_number
    assert fetched.header.invoice_date == invoice.header.invoice_date
    assert fetched.header.total_amount == invoice.header.total_amount

    # Verify items
    assert len(fetched.items) == len(invoice.items)
    assert fetched.items[0].description == invoice.items[0].description
    assert fetched.items[0].sku == invoice.items[0].sku
    assert fetched.items[0].quantity == invoice.items[0].quantity
    assert fetched.items[0].unit_price == invoice.items[0].unit_price
    assert fetched.items[0].line_total == invoice.items[0].line_total

    # Verify source
    # Note: provider is not stored in the database schema, only file_path is persisted
    if invoice.source is not None:
        assert fetched.source is not None
        assert fetched.source.file_path == invoice.source.file_path
        # provider is not persisted in the database, so it will be None after fetch

