from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import pytest

from domain.invoices import Invoice, InvoiceHeader, InvoiceItem, InvoiceSourceInfo
from storage import db as storage_db
from storage import db_async


def _make_simple_invoice(source_path: str = "") -> Invoice:
    header = InvoiceHeader(
        supplier_name="Test Supplier",
        customer_name="Test Client",
        invoice_number="INV-1",
        invoice_date=date(2024, 1, 1),
        total_amount=Decimal("1000.0"),
    )
    items = [
        InvoiceItem(
            description="Test Item",
            sku="001",
            quantity=Decimal("1.0"),
            unit_price=Decimal("1000.0"),
            line_total=Decimal("1000.0"),
        )
    ]
    source_info = InvoiceSourceInfo(
        file_path=source_path,
        provider="test",
    )
    return Invoice(
        header=header,
        items=items,
        comments=[],
        source=source_info,
    )


@pytest.mark.asyncio
async def test_save_invoice_domain_async_persists_data(tmp_path, monkeypatch) -> None:
    db_file = tmp_path / "test_async_db.sqlite"
    monkeypatch.setattr(storage_db, "DB_PATH", str(db_file), raising=True)
    monkeypatch.setattr("storage.db_async.DB_PATH", str(db_file), raising=True)

    storage_db.init_db()

    invoice = _make_simple_invoice(source_path="tests/data/invoice.pdf")

    async_id = await db_async.save_invoice_domain_async(invoice, user_id=123)

    assert async_id > 0

    from_date = date(2023, 12, 31)
    to_date = date(2024, 1, 2)

    sync_invoices = storage_db.fetch_invoices_domain(
        from_date=from_date,
        to_date=to_date,
        supplier=None,
    )

    assert len(sync_invoices) == 1
    saved = sync_invoices[0]
    assert saved.header.supplier_name == invoice.header.supplier_name
    assert saved.header.customer_name == invoice.header.customer_name
    assert saved.header.total_amount == invoice.header.total_amount
    assert len(saved.items) == len(invoice.items)
    assert saved.items[0].description == invoice.items[0].description


@pytest.mark.asyncio
async def test_fetch_invoices_domain_async_matches_sync(tmp_path, monkeypatch) -> None:
    db_file = tmp_path / "test_async_db_fetch.sqlite"
    monkeypatch.setattr(storage_db, "DB_PATH", str(db_file), raising=True)
    monkeypatch.setattr("storage.db_async.DB_PATH", str(db_file), raising=True)

    storage_db.init_db()

    base_date = date(2024, 1, 1)
    invoice1 = _make_simple_invoice()
    invoice2 = _make_simple_invoice()
    invoice2.header.invoice_date = base_date + timedelta(days=1)
    invoice2.header.supplier_name = "Other Supplier"

    storage_db.save_invoice_domain(invoice1, user_id=1)
    storage_db.save_invoice_domain(invoice2, user_id=1)

    from_date = base_date
    to_date = base_date + timedelta(days=2)

    sync_invoices = storage_db.fetch_invoices_domain(
        from_date=from_date,
        to_date=to_date,
        supplier=None,
    )

    async_invoices = await db_async.fetch_invoices_domain_async(
        from_date=from_date,
        to_date=to_date,
        supplier=None,
    )

    assert len(sync_invoices) == len(async_invoices)

    for sync_invoice, async_invoice in zip(sync_invoices, async_invoices):
        assert async_invoice.header.supplier_name == sync_invoice.header.supplier_name
        assert async_invoice.header.customer_name == sync_invoice.header.customer_name
        assert async_invoice.header.invoice_number == sync_invoice.header.invoice_number
        assert async_invoice.header.total_amount == sync_invoice.header.total_amount
        assert len(async_invoice.items) == len(sync_invoice.items)
        assert async_invoice.items[0].description == sync_invoice.items[0].description

