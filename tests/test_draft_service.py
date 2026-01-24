from __future__ import annotations

import logging
from datetime import date
from decimal import Decimal

import pytest

from backend.domain.drafts import InvoiceDraft
from backend.domain.invoices import Invoice, InvoiceHeader, InvoiceItem, InvoiceSourceInfo
from backend.services.draft_service import DraftService
from backend.storage import db as storage_db
from backend.storage.drafts_async import (
    delete_draft_invoice,
    load_draft_invoice,
    save_draft_invoice,
)


def _make_sample_draft() -> InvoiceDraft:
    header = InvoiceHeader(
        supplier_name="Test Supplier",
        customer_name="Test Client",
        invoice_number="INV-1",
        invoice_date=date(2024, 1, 1),
        total_amount=Decimal("1000.00"),
    )
    items = [
        InvoiceItem(
            description="Test item",
            sku="SKU-1",
            quantity=Decimal("1"),
            unit_price=Decimal("1000.00"),
            line_total=Decimal("1000.00"),
        )
    ]
    source_info = InvoiceSourceInfo(
        file_path="tests/data/sample.pdf",
        provider="test",
    )
    invoice = Invoice(
        header=header,
        items=items,
        comments=[],
        source=source_info,
    )
    return InvoiceDraft(
        invoice=invoice,
        path=source_info.file_path or "",
        raw_text="raw text",
        comments=["first comment"],
    )


@pytest.mark.asyncio
async def test_draft_service_roundtrip(tmp_path, monkeypatch) -> None:
    db_file = tmp_path / "test_drafts.sqlite"
    monkeypatch.setattr(storage_db, "DB_PATH", str(db_file), raising=True)
    monkeypatch.setattr("storage.drafts_async.DB_PATH", str(db_file), raising=True)

    storage_db.init_db()

    user_id = 123
    draft = _make_sample_draft()

    service = DraftService(
        load_draft_func=load_draft_invoice,
        save_draft_func=save_draft_invoice,
        delete_draft_func=delete_draft_invoice,
        logger=logging.getLogger("test"),
    )

    loaded_none = await service.get_current_draft(user_id)
    assert loaded_none is None

    await service.set_current_draft(user_id, draft)

    loaded = await service.get_current_draft(user_id)
    assert loaded is not None
    assert loaded.invoice.header.supplier_name == draft.invoice.header.supplier_name
    assert loaded.invoice.header.customer_name == draft.invoice.header.customer_name
    assert loaded.invoice.header.invoice_number == draft.invoice.header.invoice_number
    assert loaded.invoice.header.total_amount == draft.invoice.header.total_amount
    assert loaded.path == draft.path
    assert loaded.raw_text == draft.raw_text
    assert loaded.comments == draft.comments

    await service.clear_current_draft(user_id)
    loaded_after_clear = await service.get_current_draft(user_id)
    assert loaded_after_clear is None
