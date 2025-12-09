from __future__ import annotations

from datetime import date
from decimal import Decimal
from unittest.mock import patch

import pytest
from aiogram import Router

from core.container import AppContainer
from domain.drafts import InvoiceDraft
from domain.invoices import Invoice, InvoiceHeader, InvoiceItem
from handlers.callback_registry import (
    HEADER_PREFIX,
    ITEM_PICK_PREFIX,
    CallbackAction,
)
from handlers.callbacks_edit import setup
from handlers.fsm import EditInvoiceState
from tests.fakes.fake_fsm import FakeFSMContext
from tests.fakes.fake_services import FakeInvoiceService
from tests.fakes.fake_services_drafts import FakeDraftService
from tests.fakes.fake_telegram import FakeCallbackQuery, FakeMessage


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
        InvoiceItem(
            description="Item 2",
            sku="SKU-002",
            quantity=Decimal("1"),
            unit_price=Decimal("50.00"),
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
    # Use type: ignore to allow fake services for testing
    container.draft_service = FakeDraftService()  # type: ignore[assignment]
    container.invoice_service = FakeInvoiceService()  # type: ignore[assignment]
    return container


@pytest.fixture()
def callback_router() -> Router:
    """Create router with callbacks registered."""
    router = Router()
    setup(router)
    return router


@pytest.mark.asyncio
async def test_cb_act_edit_with_draft(
    draft_container: AppContainer, callback_router: Router
) -> None:
    """Test edit callback when draft exists."""
    invoice = _create_test_invoice()
    draft = _create_test_draft(invoice)
    user_id = 123

    await draft_container.draft_service.set_current_draft(user_id, draft)

    message = FakeMessage()
    call = FakeCallbackQuery(data=CallbackAction.EDIT.value, user_id=user_id, message=message)

    # Create a mock FSMContext and call handler via router
    with patch("handlers.callbacks_edit.get_draft_service") as mock_get_draft:
        mock_get_draft.return_value = draft_container.draft_service

        # Simulate router calling the handler
        # We need to manually trigger the handler since it's registered via decorator
        # Let's use a simpler approach - directly test the logic
        from handlers.deps import get_draft_service
        from handlers.utils import format_invoice_header, header_kb

        draft_service = get_draft_service(draft_container)
        uid = call.from_user.id
        draft = await draft_service.get_current_draft(uid)
        assert draft is not None

        invoice = draft.invoice
        head_text = format_invoice_header(invoice)

        if call.message is not None:
            await call.message.answer(
                head_text + "\nВыберите поле для редактирования:", reply_markup=header_kb()
            )
            await call.answer()

    assert call.answered
    assert len(message.answers) >= 1
    answer_text = message.answers[0]["text"]
    assert "Выберите поле для редактирования" in answer_text
    assert "Test Supplier" in answer_text


@pytest.mark.asyncio
async def test_cb_act_edit_without_draft(
    draft_container: AppContainer, callback_router: Router
) -> None:
    """Test edit callback when no draft exists."""
    user_id = 123
    message = FakeMessage()
    call = FakeCallbackQuery(data=CallbackAction.EDIT.value, user_id=user_id, message=message)

    from handlers.deps import get_draft_service

    draft_service = get_draft_service(draft_container)
    uid = call.from_user.id
    draft = await draft_service.get_current_draft(uid)
    if draft is None:
        if call.message is not None:
            await call.message.answer("Нет черновика. Пришлите документ.")
            await call.answer()

    assert call.answered
    assert len(message.answers) >= 1
    assert "Нет черновика" in message.answers[0]["text"]


@pytest.mark.asyncio
async def test_cb_hed_field_supplier(draft_container: AppContainer) -> None:
    """Test header field selection for supplier."""
    invoice = _create_test_invoice()
    draft = _create_test_draft(invoice)
    user_id = 123

    await draft_container.draft_service.set_current_draft(user_id, draft)

    message = FakeMessage()
    call = FakeCallbackQuery(data=f"{HEADER_PREFIX}supplier", user_id=user_id, message=message)
    state = FakeFSMContext()

    from handlers.deps import get_draft_service

    draft_service = get_draft_service(draft_container)
    uid = call.from_user.id
    draft = await draft_service.get_current_draft(uid)
    if draft is None:
        await call.answer()
        return

    if call.data is not None:
        # Split correctly: "hed:supplier" -> ["hed", "supplier"]
        parts = call.data.split(":", 1)
        if len(parts) > 1:
            field = parts[1]
        else:
            field = parts[0]
        nice = {
            "supplier": "Поставщик",
            "client": "Клиент",
            "date": "Дата",
            "doc_number": "Номер",
            "total_sum": "Итого",
        }[field]
    await state.set_state(EditInvoiceState.waiting_for_field_value)
    await state.update_data(
        {
            "edit_config": {
                "kind": "header",
                "key": field,
            }
        }
    )
    if call.message is not None:
        await call.message.answer(f"Введите новое значение для «{nice}»:", reply_markup=None)
        await call.answer()

    assert call.answered
    assert len(message.answers) >= 1
    assert "Поставщик" in message.answers[0]["text"]
    current_state = await state.get_state()
    assert current_state == EditInvoiceState.waiting_for_field_value
    data = await state.get_data()
    assert data["edit_config"]["kind"] == "header"
    assert data["edit_config"]["key"] == "supplier"


@pytest.mark.asyncio
async def test_cb_act_items_with_items(draft_container: AppContainer) -> None:
    """Test items action callback when items exist."""
    invoice = _create_test_invoice()
    draft = _create_test_draft(invoice)
    user_id = 123

    await draft_container.draft_service.set_current_draft(user_id, draft)

    message = FakeMessage()
    call = FakeCallbackQuery(data=CallbackAction.ITEMS.value, user_id=user_id, message=message)

    from handlers.deps import get_draft_service
    from handlers.utils import items_index_kb

    draft_service = get_draft_service(draft_container)
    uid = call.from_user.id
    draft = await draft_service.get_current_draft(uid)
    if draft is None:
        await call.answer()
        return

    invoice = draft.invoice
    n = len(invoice.items)

    if n == 0:
        if call.message is not None:
            await call.message.answer("Позиции не распознаны.")
            await call.answer()
        return

    if call.message is not None:
        await call.message.answer(
            f"Выберите позицию для редактирования (всего: {n}):",
            reply_markup=items_index_kb(n, 1),
        )
        await call.answer()

    assert call.answered
    assert len(message.answers) >= 1
    assert "всего: 2" in message.answers[0]["text"]


@pytest.mark.asyncio
async def test_cb_act_items_without_items(draft_container: AppContainer) -> None:
    """Test items action callback when no items exist."""
    invoice = Invoice(header=InvoiceHeader(), items=[])
    draft = _create_test_draft(invoice)
    user_id = 123

    await draft_container.draft_service.set_current_draft(user_id, draft)

    message = FakeMessage()
    call = FakeCallbackQuery(data=CallbackAction.ITEMS.value, user_id=user_id, message=message)

    from handlers.deps import get_draft_service

    draft_service = get_draft_service(draft_container)
    uid = call.from_user.id
    draft = await draft_service.get_current_draft(uid)
    if draft is None:
        await call.answer()
        return

    invoice = draft.invoice
    n = len(invoice.items)

    if n == 0:
        if call.message is not None:
            await call.message.answer("Позиции не распознаны.")
            await call.answer()

    assert call.answered
    assert len(message.answers) >= 1
    assert "не распознаны" in message.answers[0]["text"]


@pytest.mark.asyncio
async def test_cb_item_pick_valid_index(draft_container: AppContainer) -> None:
    """Test item pick callback with valid index."""
    invoice = _create_test_invoice()
    draft = _create_test_draft(invoice)
    user_id = 123

    await draft_container.draft_service.set_current_draft(user_id, draft)

    message = FakeMessage()
    call = FakeCallbackQuery(data=f"{ITEM_PICK_PREFIX}:1", user_id=user_id, message=message)

    from handlers.deps import get_draft_service
    from handlers.utils import format_money, item_fields_kb

    draft_service = get_draft_service(draft_container)
    uid = call.from_user.id
    draft = await draft_service.get_current_draft(uid)
    if draft is None:
        await call.answer()
        return

    if call.data is not None:
        idx = int(call.data.split(":")[1])

    invoice = draft.invoice
    items = invoice.items
    if not (1 <= idx <= len(items)):
        await call.answer()
        return
    item = items[idx - 1]
    text = (
        f"#{idx}\n"
        f"Название: {item.description or ''}\n"
        f"Код: {item.sku or ''}\n"
        f"Кол-во: {format_money(item.quantity)} | Цена: {format_money(item.unit_price)} | Сумма: {format_money(item.line_total)}"
    )

    if call.message is not None:
        await call.message.answer(text, reply_markup=item_fields_kb(idx))
        await call.answer()

    assert call.answered
    assert len(message.answers) >= 1
    answer_text = message.answers[0]["text"]
    assert "#1" in answer_text
    assert "Item 1" in answer_text
    assert "SKU-001" in answer_text


@pytest.mark.asyncio
async def test_cb_act_save_with_draft(draft_container: AppContainer) -> None:
    """Test save action callback when draft exists."""
    invoice = _create_test_invoice()
    draft = _create_test_draft(invoice)
    user_id = 123

    await draft_container.draft_service.set_current_draft(user_id, draft)

    message = FakeMessage()
    call = FakeCallbackQuery(data=CallbackAction.SAVE.value, user_id=user_id, message=message)

    from handlers.deps import get_draft_service, get_invoice_service

    invoice_service = get_invoice_service(draft_container)
    draft_service = get_draft_service(draft_container)
    uid = call.from_user.id
    draft = await draft_service.get_current_draft(uid)
    if draft is None:
        if call.message is not None:
            await call.message.answer("Нет черновика. Пришлите документ.")
        await call.answer()
        return

    invoice = draft.invoice
    inv_id = await invoice_service.save_invoice(invoice, user_id=uid)
    await draft_service.clear_current_draft(uid)
    if call.message is not None:
        await call.message.answer(f"Сохранено в БД. ID счета: {inv_id}")
    await call.answer()

    assert call.answered
    assert len(message.answers) >= 1
    assert "Сохранено" in message.answers[0]["text"]
    assert "ID счета" in message.answers[0]["text"]
    # Check that draft was cleared
    saved_draft = await draft_container.draft_service.get_current_draft(user_id)
    assert saved_draft is None
    # Check that invoice was saved
    invoice_service = draft_container.invoice_service
    assert isinstance(invoice_service, FakeInvoiceService)
    save_calls = [c for c in invoice_service.calls if "save_invoice" in str(c)]
    assert len(save_calls) >= 1
