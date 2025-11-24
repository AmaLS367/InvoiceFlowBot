"""
Integration tests for CRUD operations on invoices using AsyncInvoiceStorage.

These tests verify the full flow of creating, reading, updating, and querying invoices
against a real SQLite database with Alembic migrations applied.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import List

import pytest

from domain.invoices import Invoice, InvoiceHeader, InvoiceItem
from storage.db_async import AsyncInvoiceStorage

pytestmark = pytest.mark.storage_db


@pytest.mark.asyncio
async def test_save_and_fetch_invoice_by_date_range(
    async_storage_with_migrations: AsyncInvoiceStorage,
) -> None:
    """
    Test saving an invoice and retrieving it by date range.

    Since AsyncInvoiceStorage doesn't have get_invoice_by_id, we use fetch_invoices
    with a date range that includes our invoice.
    """
    storage = async_storage_with_migrations

    items: List[InvoiceItem] = [
        InvoiceItem(
            description="Item 1",
            sku="SKU-001",
            quantity=Decimal("2.0"),
            unit_price=Decimal("10.0"),
            line_total=Decimal("20.0"),
        ),
        InvoiceItem(
            description="Item 2",
            sku="SKU-002",
            quantity=Decimal("1.0"),
            unit_price=Decimal("5.0"),
            line_total=Decimal("5.0"),
        ),
    ]

    header = InvoiceHeader(
        supplier_name="Test supplier",
        customer_name="Test customer",
        invoice_number="INV-001",
        invoice_date=date(2025, 1, 15),
        total_amount=Decimal("25.0"),
    )

    invoice = Invoice(
        header=header,
        items=items,
        comments=[],
        source=None,
    )

    invoice_id = await storage.save_invoice(invoice, user_id=123)

    assert invoice_id > 0

    # Fetch invoice by date range
    from_date = date(2025, 1, 1)
    to_date = date(2025, 1, 31)

    fetched_invoices = await storage.fetch_invoices(
        from_date=from_date,
        to_date=to_date,
        supplier=None,
    )

    assert len(fetched_invoices) >= 1

    # Find our invoice by invoice_number
    loaded_invoice = None
    for inv in fetched_invoices:
        if inv.header.invoice_number == invoice.header.invoice_number:
            loaded_invoice = inv
            break

    assert loaded_invoice is not None
    assert loaded_invoice.header.supplier_name == invoice.header.supplier_name
    assert loaded_invoice.header.customer_name == invoice.header.customer_name
    assert loaded_invoice.header.invoice_number == invoice.header.invoice_number
    assert loaded_invoice.header.invoice_date == invoice.header.invoice_date
    assert loaded_invoice.header.total_amount == invoice.header.total_amount

    assert len(loaded_invoice.items) == len(items)
    assert loaded_invoice.items[0].description == items[0].description
    assert loaded_invoice.items[0].sku == items[0].sku
    assert loaded_invoice.items[0].quantity == items[0].quantity
    assert loaded_invoice.items[0].unit_price == items[0].unit_price
    assert loaded_invoice.items[0].line_total == items[0].line_total
    assert loaded_invoice.items[1].description == items[1].description
    assert loaded_invoice.items[1].line_total == items[1].line_total


@pytest.mark.asyncio
async def test_list_invoices_returns_saved_invoices(
    async_storage_with_migrations: AsyncInvoiceStorage,
) -> None:
    """
    Test that fetch_invoices returns all saved invoices when called without filters.

    We use fetch_invoices with None dates to get all invoices.
    """
    storage = async_storage_with_migrations

    invoices: List[Invoice] = []
    for i in range(3):
        items: List[InvoiceItem] = [
            InvoiceItem(
                description=f"Item {i}",
                sku=f"SKU-{i:03d}",
                quantity=Decimal("1.0"),
                unit_price=Decimal("10.0"),
                line_total=Decimal("10.0"),
            ),
        ]

        header = InvoiceHeader(
            supplier_name=f"Supplier {i}",
            customer_name=f"Customer {i}",
            invoice_number=f"INV-{i + 1:03d}",
            invoice_date=date(2025, 2, i + 1),
            total_amount=Decimal("10.0"),
        )

        invoice = Invoice(
            header=header,
            items=items,
            comments=[],
            source=None,
        )
        invoices.append(invoice)
        await storage.save_invoice(invoice, user_id=123)

    # Fetch all invoices (no date filter)
    all_invoices = await storage.fetch_invoices(
        from_date=None,
        to_date=None,
        supplier=None,
    )

    assert len(all_invoices) >= 3

    loaded = {inv.header.invoice_number: inv for inv in all_invoices}

    for invoice in invoices:
        assert invoice.header.invoice_number in loaded
        loaded_invoice = loaded[invoice.header.invoice_number]
        assert loaded_invoice.header.supplier_name == invoice.header.supplier_name
        assert loaded_invoice.header.customer_name == invoice.header.customer_name
        assert loaded_invoice.header.invoice_date == invoice.header.invoice_date
        assert loaded_invoice.header.total_amount == invoice.header.total_amount


@pytest.mark.asyncio
async def test_fetch_invoices_by_supplier_filters_results(
    async_storage_with_migrations: AsyncInvoiceStorage,
) -> None:
    """
    Test that fetch_invoices correctly filters by supplier name.
    """
    storage = async_storage_with_migrations

    header_1 = InvoiceHeader(
        supplier_name="Supplier A",
        customer_name="Customer 1",
        invoice_number="INV-A-001",
        invoice_date=date(2025, 3, 1),
        total_amount=Decimal("100.0"),
    )

    invoice_1 = Invoice(
        header=header_1,
        items=[],
        comments=[],
        source=None,
    )

    header_2 = InvoiceHeader(
        supplier_name="Supplier B",
        customer_name="Customer 2",
        invoice_number="INV-B-001",
        invoice_date=date(2025, 3, 2),
        total_amount=Decimal("200.0"),
    )

    invoice_2 = Invoice(
        header=header_2,
        items=[],
        comments=[],
        source=None,
    )

    await storage.save_invoice(invoice_1, user_id=123)
    await storage.save_invoice(invoice_2, user_id=123)

    # Fetch invoices for Supplier A
    from_date = date(2025, 2, 1)
    to_date = date(2025, 3, 31)

    supplier_a_invoices = await storage.fetch_invoices(
        from_date=from_date,
        to_date=to_date,
        supplier="Supplier A",
    )

    assert len(supplier_a_invoices) >= 1
    assert all(inv.header.supplier_name == "Supplier A" for inv in supplier_a_invoices)

    # Verify we can find our invoice
    invoice_numbers = {inv.header.invoice_number for inv in supplier_a_invoices}
    assert "INV-A-001" in invoice_numbers


@pytest.mark.asyncio
async def test_save_invoice_creates_new_record_each_time(
    async_storage_with_migrations: AsyncInvoiceStorage,
) -> None:
    """
    Test that save_invoice always creates a new record (INSERT behavior).

    Since save_invoice doesn't support updates, calling it twice with the same
    invoice_number should create two separate records.
    """
    storage = async_storage_with_migrations

    items: List[InvoiceItem] = [
        InvoiceItem(
            description="Original",
            sku="SKU-ORIG",
            quantity=Decimal("1.0"),
            unit_price=Decimal("10.0"),
            line_total=Decimal("10.0"),
        )
    ]

    header = InvoiceHeader(
        supplier_name="Supplier X",
        customer_name="Customer X",
        invoice_number="INV-X-001",
        invoice_date=date(2025, 4, 1),
        total_amount=Decimal("10.0"),
    )

    invoice = Invoice(
        header=header,
        items=items,
        comments=[],
        source=None,
    )

    invoice_id_1 = await storage.save_invoice(invoice, user_id=123)
    assert invoice_id_1 > 0

    # Save again with same invoice_number but different data
    updated_items: List[InvoiceItem] = [
        InvoiceItem(
            description="Updated item",
            sku="SKU-UPD",
            quantity=Decimal("2.0"),
            unit_price=Decimal("15.0"),
            line_total=Decimal("30.0"),
        )
    ]

    updated_header = InvoiceHeader(
        supplier_name="Supplier X updated",
        customer_name="Customer X updated",
        invoice_number="INV-X-001",  # Same invoice number
        invoice_date=date(2025, 4, 2),
        total_amount=Decimal("30.0"),
    )

    updated_invoice = Invoice(
        header=updated_header,
        items=updated_items,
        comments=[],
        source=None,
    )

    invoice_id_2 = await storage.save_invoice(updated_invoice, user_id=123)
    assert invoice_id_2 > 0
    assert invoice_id_2 != invoice_id_1  # Should be a different record

    # Fetch all invoices with this invoice_number
    from_date = date(2025, 3, 1)
    to_date = date(2025, 4, 30)

    fetched_invoices = await storage.fetch_invoices(
        from_date=from_date,
        to_date=to_date,
        supplier="Supplier X",
    )

    # Should have at least 2 invoices with this supplier
    assert len(fetched_invoices) >= 2

    # Both should have the same invoice_number but different data
    invoices_with_number = [
        inv for inv in fetched_invoices if inv.header.invoice_number == "INV-X-001"
    ]
    assert len(invoices_with_number) >= 2

    # Verify they have different data
    suppliers = {inv.header.supplier_name for inv in invoices_with_number}
    assert "Supplier X" in suppliers
    assert "Supplier X updated" in suppliers


@pytest.mark.asyncio
async def test_save_invoice_without_items(
    async_storage_with_migrations: AsyncInvoiceStorage,
) -> None:
    """
    Test saving an invoice with no items (empty items list).

    This is an edge case to ensure the code handles empty lists correctly.
    """
    storage = async_storage_with_migrations

    header = InvoiceHeader(
        supplier_name="No Items Supplier",
        customer_name="No Items Customer",
        invoice_number="INV-NOITEMS",
        invoice_date=date(2025, 5, 1),
        total_amount=Decimal("0.0"),
    )

    invoice = Invoice(
        header=header,
        items=[],
        comments=[],
        source=None,
    )

    invoice_id = await storage.save_invoice(invoice, user_id=123)
    assert invoice_id > 0

    # Fetch invoice
    from_date = date(2025, 4, 1)
    to_date = date(2025, 5, 31)

    fetched_invoices = await storage.fetch_invoices(
        from_date=from_date,
        to_date=to_date,
        supplier="No Items Supplier",
    )

    assert len(fetched_invoices) >= 1

    # Find our invoice
    loaded_invoice = None
    for inv in fetched_invoices:
        if inv.header.invoice_number == "INV-NOITEMS":
            loaded_invoice = inv
            break

    assert loaded_invoice is not None
    assert loaded_invoice.header.supplier_name == invoice.header.supplier_name
    assert loaded_invoice.header.customer_name == invoice.header.customer_name
    assert loaded_invoice.header.invoice_number == invoice.header.invoice_number
    assert len(loaded_invoice.items) == 0


@pytest.mark.asyncio
async def test_fetch_invoices_with_date_range(
    async_storage_with_migrations: AsyncInvoiceStorage,
) -> None:
    """
    Test that fetch_invoices correctly filters by date range.
    """
    storage = async_storage_with_migrations

    # Create invoices on different dates
    invoices: List[Invoice] = []
    for i in range(5):
        header = InvoiceHeader(
            supplier_name="Date Test Supplier",
            customer_name=f"Customer {i}",
            invoice_number=f"INV-DATE-{i:03d}",
            invoice_date=date(2025, 6, i + 1),  # June 1-5
            total_amount=Decimal(f"{100.0 + i * 10}"),
        )

        invoice = Invoice(
            header=header,
            items=[],
            comments=[],
            source=None,
        )
        invoices.append(invoice)
        await storage.save_invoice(invoice, user_id=123)

    # Fetch invoices for June 2-4
    from_date = date(2025, 6, 2)
    to_date = date(2025, 6, 4)

    fetched_invoices = await storage.fetch_invoices(
        from_date=from_date,
        to_date=to_date,
        supplier="Date Test Supplier",
    )

    # Should have 3 invoices (June 2, 3, 4)
    assert len(fetched_invoices) >= 3

    # Verify dates are in range
    for inv in fetched_invoices:
        if inv.header.invoice_date:
            assert from_date <= inv.header.invoice_date <= to_date

    # Verify we have the expected invoices
    invoice_numbers = {inv.header.invoice_number for inv in fetched_invoices}
    assert "INV-DATE-001" in invoice_numbers  # June 2
    assert "INV-DATE-002" in invoice_numbers  # June 3
    assert "INV-DATE-003" in invoice_numbers  # June 4
