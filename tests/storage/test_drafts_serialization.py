from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

import pytest

from backend.domain.drafts import InvoiceDraft
from backend.domain.invoices import (
    Invoice,
    InvoiceComment,
    InvoiceHeader,
    InvoiceItem,
    InvoiceSourceInfo,
)
from backend.storage import db as storage_db
from backend.storage.db_async import AsyncInvoiceStorage
from backend.storage.drafts_async import load_draft_invoice, save_draft_invoice
from tests.utils.alembic_test_utils import run_migrations_for_url

pytestmark = pytest.mark.storage_db


@pytest.mark.asyncio
async def test_draft_sqlite_round_trip_preserves_all_fields(tmp_path: Path) -> None:
    db_path = tmp_path / "drafts.sqlite3"
    run_migrations_for_url(f"sqlite:///{db_path}")

    header = InvoiceHeader(
        supplier_name="Supplier SA",
        customer_name="Client LLC",
        invoice_number="INV-2025-001",
        invoice_date=date(2025, 6, 15),
        total_amount=Decimal("74.50"),
    )
    items = [
        InvoiceItem(
            description="Spinach",
            sku="EP001",
            quantity=Decimal("2"),
            unit_price=Decimal("2.35"),
            line_total=Decimal("4.70"),
        ),
        InvoiceItem(
            description="Cucumber",
            sku="CO002",
            quantity=Decimal("5"),
            unit_price=Decimal("0.89"),
            line_total=Decimal("4.45"),
        ),
    ]
    source = InvoiceSourceInfo(provider="mindee")
    invoice = Invoice(
        header=header,
        items=items,
        comments=[],
        source=source,
    )
    draft = InvoiceDraft(
        invoice=invoice,
        path="/tmp/test_invoice.pdf",
        raw_text="",
        comments=["First comment", "Second comment"],
    )

    user_id = 42
    with (
        patch.object(storage_db, "DB_PATH", str(db_path)),
        patch("backend.storage.drafts_async.DB_PATH", str(db_path)),
    ):
        await save_draft_invoice(user_id, draft)
        loaded = await load_draft_invoice(user_id)

    assert loaded is not None
    assert loaded.path == "/tmp/test_invoice.pdf"
    assert loaded.comments == ["First comment", "Second comment"]

    header_loaded = loaded.invoice.header
    assert header_loaded.supplier_name == "Supplier SA"
    assert header_loaded.customer_name == "Client LLC"
    assert header_loaded.invoice_number == "INV-2025-001"
    assert header_loaded.invoice_date == date(2025, 6, 15)
    assert header_loaded.total_amount == Decimal("74.50")

    assert len(loaded.invoice.items) == 2
    assert loaded.invoice.items[0].description == "Spinach"
    assert loaded.invoice.items[0].sku == "EP001"
    assert loaded.invoice.items[0].quantity == Decimal("2")
    assert loaded.invoice.items[0].unit_price == Decimal("2.35")
    assert loaded.invoice.items[0].line_total == Decimal("4.70")
    assert loaded.invoice.items[1].description == "Cucumber"
    assert loaded.invoice.items[1].sku == "CO002"


@pytest.mark.asyncio
async def test_fetch_invoices_loads_saved_comments(tmp_path: Path) -> None:
    db_path = tmp_path / "invoices_comments.sqlite3"
    run_migrations_for_url(f"sqlite:///{db_path}")

    invoice = Invoice(
        header=InvoiceHeader(
            supplier_name="Supplier SA",
            customer_name="Client LLC",
            invoice_number="INV-CMT-1",
            invoice_date=date(2025, 6, 15),
            total_amount=Decimal("100.00"),
        ),
        items=[
            InvoiceItem(
                description="Item A",
                sku="A1",
                quantity=Decimal("1"),
                unit_price=Decimal("100.00"),
                line_total=Decimal("100.00"),
            )
        ],
        comments=[
            InvoiceComment(message="Manual comment", author="42"),
            InvoiceComment(message="[auto] Check total", author="42"),
        ],
    )

    storage = AsyncInvoiceStorage(database_path=str(db_path))
    await storage.save_invoice(invoice, user_id=42)

    fetched = await storage.fetch_invoices(date(2025, 6, 1), date(2025, 6, 30))
    assert len(fetched) == 1
    assert [c.message for c in fetched[0].comments] == [
        "Manual comment",
        "[auto] Check total",
    ]
    assert fetched[0].comments[0].author == "42"
