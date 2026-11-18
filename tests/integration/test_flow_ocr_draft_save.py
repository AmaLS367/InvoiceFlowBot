from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import List

import pytest

from backend.core.container import AppContainer
from backend.domain.drafts import InvoiceDraft
from backend.domain.invoices import Invoice, InvoiceComment, InvoiceHeader
from backend.handlers import texts
from backend.handlers.commands_invoices import cmd_invoices, handle_force_reply_invoices
from backend.handlers.fsm import InvoicesPeriodState
from backend.ocr.engine.types import ExtractionResult, Item
from tests.fakes.fake_fsm import FakeFSMContext
from tests.fakes.fake_ocr import FakeOcr
from tests.fakes.fake_telegram import FakeMessage

pytestmark = pytest.mark.storage_db


def _get_fake_ocr(container: AppContainer) -> FakeOcr:
    if hasattr(container, "_fake_ocr"):
        return container._fake_ocr  # type: ignore[attr-defined]
    raise RuntimeError("FakeOcr not accessible from container")


@pytest.mark.asyncio
async def test_full_flow_ocr_draft_save_and_query(
    integration_flow_container: AppContainer,
) -> None:
    container = integration_flow_container

    user_id = 123
    file_path = "test_invoice.pdf"

    expected_items: List[Item] = [
        Item(
            code="SKU-001",
            name="Item 1",
            qty=2.0,
            price=10.0,
            total=20.0,
        ),
        Item(
            code="SKU-002",
            name="Item 2",
            qty=1.0,
            price=5.0,
            total=5.0,
        ),
    ]

    expected_extraction_result = ExtractionResult(
        document_id="test-doc-id",
        supplier="Flow supplier",
        client="Flow customer",
        date="2025-07-01",
        total_sum=25.0,
        template="mindee",
        items=expected_items,
        pages=[],
        warnings=[],
    )

    async def test_extractor(
        pdf_path: str, fast: bool = True, max_pages: int = 12
    ) -> ExtractionResult:
        return expected_extraction_result

    container.invoice_service._ocr_extractor = test_extractor  # type: ignore[attr-defined]

    invoice = await container.invoice_service.process_invoice_file(
        pdf_path=file_path,
        fast=True,
        max_pages=12,
    )

    assert invoice is not None
    assert invoice.header.supplier_name == "Flow supplier"
    assert invoice.header.customer_name == "Flow customer"
    assert invoice.header.total_amount == Decimal("25.0")
    assert len(invoice.items) == 2
    assert invoice.items[0].description == "Item 1"
    assert invoice.items[0].quantity == Decimal("2.0")
    assert invoice.items[0].unit_price == Decimal("10.0")
    assert invoice.items[0].line_total == Decimal("20.0")

    draft = InvoiceDraft(
        invoice=invoice,
        path=file_path,
        raw_text="",
        comments=[],
    )
    await container.draft_service.set_current_draft(user_id=user_id, draft=draft)

    loaded_draft = await container.draft_service.get_current_draft(user_id)
    assert loaded_draft is not None
    assert loaded_draft.invoice.header.supplier_name == "Flow supplier"
    assert len(loaded_draft.invoice.items) == 2

    invoice_to_save = loaded_draft.invoice
    invoice_id = await container.invoice_service.save_invoice(invoice_to_save, user_id=user_id)

    assert invoice_id > 0

    await container.draft_service.clear_current_draft(user_id)

    cleared_draft = await container.draft_service.get_current_draft(user_id)
    assert cleared_draft is None

    from_date = date(2025, 7, 1)
    to_date = date(2025, 7, 31)
    invoices = await container.invoice_service.list_invoices(
        user_id=user_id,
        from_date=from_date,
        to_date=to_date,
        supplier=None,
    )

    assert len(invoices) >= 1

    loaded_invoice = next(
        (inv for inv in invoices if inv.header.supplier_name == "Flow supplier"),
        None,
    )
    assert loaded_invoice is not None

    assert loaded_invoice.header.supplier_name == "Flow supplier"
    assert loaded_invoice.header.customer_name == "Flow customer"
    assert loaded_invoice.header.total_amount == Decimal("25.0")

    assert len(loaded_invoice.items) == 2
    assert loaded_invoice.items[0].description == "Item 1"
    assert loaded_invoice.items[0].sku == "SKU-001"
    assert loaded_invoice.items[0].quantity == Decimal("2.0")
    assert loaded_invoice.items[0].unit_price == Decimal("10.0")
    assert loaded_invoice.items[0].line_total == Decimal("20.0")

    assert loaded_invoice.items[1].description == "Item 2"
    assert loaded_invoice.items[1].sku == "SKU-002"
    assert loaded_invoice.items[1].quantity == Decimal("1.0")
    assert loaded_invoice.items[1].unit_price == Decimal("5.0")
    assert loaded_invoice.items[1].line_total == Decimal("5.0")


@pytest.mark.asyncio
@pytest.mark.parametrize("use_period_reply", [False, True])
async def test_invoice_handlers_only_show_senders_invoices(
    integration_flow_container: AppContainer,
    use_period_reply: bool,
) -> None:
    container = integration_flow_container
    records = [(123, "North", "42.25", "Paid by transfer"), (456, "South", "87.75", "Paid in cash")]
    for user_id, supplier, total, comment in records:
        invoice = Invoice(
            header=InvoiceHeader(
                supplier_name=f"Shared {supplier}",
                invoice_date=date(2025, 7, 10),
                total_amount=Decimal(total),
            ),
            comments=[InvoiceComment(message=comment)],
        )
        await container.invoice_service.save_invoice(invoice, user_id=user_id)

    for (user_id, supplier, total, comment), (_, other_supplier, other_total, other_comment) in zip(
        records, reversed(records), strict=True
    ):
        if use_period_reply:
            message = FakeMessage(text="Shared", user_id=user_id, chat_id=-10)
            state = FakeFSMContext()
            await state.set_state(InvoicesPeriodState.waiting_for_supplier)
            await state.update_data({"period": {"from": "2025-07-01", "to": "2025-07-31"}})
            assert await handle_force_reply_invoices(message, state, container)
        else:
            message = FakeMessage(
                text="/invoices 2025-07-01 2025-07-31 supplier=Shared", user_id=user_id, chat_id=-10
            )
            await cmd_invoices(message, container)

        assert len(message.answers) == 1
        answer = message.answers[0]["text"]
        assert f"Shared {supplier}" in answer
        assert comment in answer
        assert f"Shared {other_supplier}" not in answer
        assert other_total not in answer
        assert other_comment not in answer
        assert answer.endswith(f"{texts.t('INVOICES_TOTAL_LABEL')}: {total}")
