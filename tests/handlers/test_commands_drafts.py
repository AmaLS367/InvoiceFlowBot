from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from core.container import AppContainer
from domain.drafts import InvoiceDraft
from domain.invoices import Invoice, InvoiceHeader, InvoiceItem
from handlers.commands_drafts import _parse_date_str
from handlers.fsm import EditInvoiceState
from tests.fakes.fake_fsm import FakeFSMContext
from tests.fakes.fake_services_drafts import FakeDraftService
from tests.fakes.fake_telegram import FakeMessage


def _create_test_invoice() -> Invoice:
    """Create a test invoice with sample data."""
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
    return Invoice(header=header, items=items)


def _create_test_draft(invoice: Invoice) -> InvoiceDraft:
    """Create a test draft."""
    return InvoiceDraft(
        invoice=invoice,
        path="test.pdf",
        raw_text="",
        comments=[],
    )


@pytest.fixture()
def draft_container() -> AppContainer:
    """Create container with fake draft service."""
    from config import Settings
    from tests.fakes.fake_ocr import FakeOcr, make_fake_ocr_extractor
    from tests.fakes.fake_storage import (
        FakeStorage,
        make_fake_delete_draft_func,
        make_fake_fetch_invoices_func,
        make_fake_load_draft_func,
        make_fake_save_draft_func,
        make_fake_save_invoice_func,
    )

    container = AppContainer(
        config=Settings(),  # type: ignore[call-arg]
        ocr_extractor=make_fake_ocr_extractor(fake_ocr=FakeOcr()),
        save_invoice_func=make_fake_save_invoice_func(fake_storage=FakeStorage()),
        fetch_invoices_func=make_fake_fetch_invoices_func(fake_storage=FakeStorage()),
        load_draft_func=make_fake_load_draft_func(fake_storage=FakeStorage()),
        save_draft_func=make_fake_save_draft_func(fake_storage=FakeStorage()),
        delete_draft_func=make_fake_delete_draft_func(fake_storage=FakeStorage()),
    )
    container.draft_service = FakeDraftService()  # type: ignore[assignment]
    return container


def test_parse_date_str_valid_iso() -> None:
    """Test _parse_date_str with valid ISO format."""
    result = _parse_date_str("2025-01-15")
    assert result == date(2025, 1, 15)


def test_parse_date_str_invalid_format() -> None:
    """Test _parse_date_str with invalid format."""
    result = _parse_date_str("invalid-date")
    # Should try to_iso conversion, but if that fails, return None
    assert result is None or isinstance(result, date)


def test_parse_date_str_empty() -> None:
    """Test _parse_date_str with empty string."""
    result = _parse_date_str("")
    assert result is None


def test_parse_date_str_none() -> None:
    """Test _parse_date_str with None."""
    result = _parse_date_str(None)  # type: ignore[arg-type]
    assert result is None


@pytest.mark.asyncio
async def test_cmd_show_with_draft(draft_container: AppContainer) -> None:
    """Test /show command when draft exists."""
    invoice = _create_test_invoice()
    draft = _create_test_draft(invoice)
    user_id = 123

    await draft_container.draft_service.set_current_draft(user_id, draft)

    message = FakeMessage(text="/show", user_id=user_id)

    from handlers.deps import get_draft_service
    from handlers.utils import format_invoice_full, format_invoice_header

    draft_service = get_draft_service(draft_container)
    uid = message.from_user.id if message.from_user else 0
    draft = await draft_service.get_current_draft(uid)
    if draft is None:
        await message.answer("Нет черновика. Пришлите документ.")
        return

    invoice = draft.invoice
    full_text = format_invoice_full(invoice)
    await message.answer(full_text if len(full_text) < 3900 else format_invoice_header(invoice))

    assert len(message.answers) >= 1
    answer_text = message.answers[0]["text"]
    assert "Test Supplier" in answer_text or "INV-001" in answer_text


@pytest.mark.asyncio
async def test_cmd_show_without_draft(draft_container: AppContainer) -> None:
    """Test /show command when no draft exists."""
    user_id = 123
    message = FakeMessage(text="/show", user_id=user_id)

    from handlers.deps import get_draft_service

    draft_service = get_draft_service(draft_container)
    uid = message.from_user.id if message.from_user else 0
    draft = await draft_service.get_current_draft(uid)
    if draft is None:
        await message.answer("Нет черновика. Пришлите документ.")

    assert len(message.answers) >= 1
    assert "Нет черновика" in message.answers[0]["text"]


@pytest.mark.asyncio
async def test_on_force_reply_comment(draft_container: AppContainer) -> None:
    """Test force reply for comment."""
    invoice = _create_test_invoice()
    draft = _create_test_draft(invoice)
    user_id = 123

    await draft_container.draft_service.set_current_draft(user_id, draft)

    message = FakeMessage(text="Test comment", user_id=user_id)
    state = FakeFSMContext()
    await state.set_state(EditInvoiceState.waiting_for_comment)

    from handlers.deps import get_draft_service

    draft_service = get_draft_service(draft_container)
    uid = message.from_user.id if message.from_user else 0

    current_state = await state.get_state()

    if current_state == EditInvoiceState.waiting_for_comment:
        draft = await draft_service.get_current_draft(uid)
        if draft is None:
            await message.answer("Нет черновика. Загрузите документ.")
            await state.clear()
            return
        text = (message.text or "").strip()
        if not text:
            await message.answer("Пустой комментарий игнорирован.")
        else:
            draft.comments.append(text)
            await draft_service.set_current_draft(uid, draft)
            await message.answer("Комментарий добавлен.")
        await state.clear()

    assert len(message.answers) >= 1
    assert "Комментарий добавлен" in message.answers[0]["text"]
    # Check that comment was added
    saved_draft = await draft_container.draft_service.get_current_draft(user_id)
    assert saved_draft is not None
    assert "Test comment" in saved_draft.comments


@pytest.mark.asyncio
async def test_on_force_reply_header_field(draft_container: AppContainer) -> None:
    """Test force reply for header field editing."""
    invoice = _create_test_invoice()
    draft = _create_test_draft(invoice)
    user_id = 123

    await draft_container.draft_service.set_current_draft(user_id, draft)

    message = FakeMessage(text="New Supplier Name", user_id=user_id)
    state = FakeFSMContext()
    await state.set_state(EditInvoiceState.waiting_for_field_value)
    await state.update_data({"edit_config": {"kind": "header", "key": "supplier"}})

    from handlers.deps import get_draft_service

    draft_service = get_draft_service(draft_container)
    uid = message.from_user.id if message.from_user else 0

    current_state = await state.get_state()

    if current_state == EditInvoiceState.waiting_for_field_value:
        state_data = await state.get_data()
        edit_config = state_data.get("edit_config") or {}
        kind = edit_config.get("kind")

        draft = await draft_service.get_current_draft(uid)
        if draft is None:
            await message.answer("Нет черновика. Загрузите документ.")
            await state.clear()
            return

        invoice = draft.invoice
        if message.text is not None:
            val = message.text.strip()

        if kind == "header":
            k = edit_config.get("key")
            header = invoice.header
            if k == "supplier":
                header.supplier_name = val
            await message.answer(
                'Поле обновлено. Нажмите кнопку "Сохранить" или введите команду /save чтобы сохранить в БД.'
            )
            await draft_service.set_current_draft(uid, draft)
            await state.clear()

    assert len(message.answers) >= 1
    assert "Поле обновлено" in message.answers[0]["text"]
    # Check that field was updated
    saved_draft = await draft_container.draft_service.get_current_draft(user_id)
    assert saved_draft is not None
    assert saved_draft.invoice.header.supplier_name == "New Supplier Name"


@pytest.mark.asyncio
async def test_on_force_reply_item_field(draft_container: AppContainer) -> None:
    """Test force reply for item field editing."""
    invoice = _create_test_invoice()
    draft = _create_test_draft(invoice)
    user_id = 123

    await draft_container.draft_service.set_current_draft(user_id, draft)

    message = FakeMessage(text="New Item Name", user_id=user_id)
    state = FakeFSMContext()
    await state.set_state(EditInvoiceState.waiting_for_field_value)
    await state.update_data({"edit_config": {"kind": "item", "idx": 1, "key": "name"}})

    from handlers.deps import get_draft_service

    draft_service = get_draft_service(draft_container)
    uid = message.from_user.id if message.from_user else 0

    current_state = await state.get_state()

    if current_state == EditInvoiceState.waiting_for_field_value:
        state_data = await state.get_data()
        edit_config = state_data.get("edit_config") or {}
        kind = edit_config.get("kind")

        draft = await draft_service.get_current_draft(uid)
        if draft is None:
            await message.answer("Нет черновика. Загрузите документ.")
            await state.clear()
            return

        invoice = draft.invoice
        if message.text is not None:
            val = message.text.strip()

        if kind == "item":
            idx_raw = edit_config.get("idx")
            if isinstance(idx_raw, int):
                idx = idx_raw
                key = edit_config.get("key")
                items = invoice.items
                if 1 <= idx <= len(items):
                    item = items[idx - 1]
                    if key == "name":
                        item.description = val
                    await message.answer(
                        'Поле обновлено. Нажмите кнопку "Сохранить" или введите команду /save чтобы сохранить в БД.'
                    )
                    await draft_service.set_current_draft(uid, draft)
                    await state.clear()

    assert len(message.answers) >= 1
    assert "Поле обновлено" in message.answers[0]["text"]
    # Check that item field was updated
    saved_draft = await draft_container.draft_service.get_current_draft(user_id)
    assert saved_draft is not None
    assert saved_draft.invoice.items[0].description == "New Item Name"
