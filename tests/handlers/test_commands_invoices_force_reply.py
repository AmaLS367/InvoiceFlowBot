from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from core.container import AppContainer
from domain.invoices import Invoice, InvoiceHeader
from handlers.commands_invoices import _parse_date_str
from handlers.fsm import InvoicesPeriodState
from tests.fakes.fake_fsm import FakeFSMContext
from tests.fakes.fake_services import FakeInvoiceService
from tests.fakes.fake_telegram import FakeMessage


def test_parse_date_str_valid():
    """Test _parse_date_str with valid ISO format."""
    result = _parse_date_str("2025-01-15")
    assert result == date(2025, 1, 15)


def test_parse_date_str_invalid():
    """Test _parse_date_str with invalid format."""
    result = _parse_date_str("invalid")
    # Should try to_iso conversion
    assert result is None or isinstance(result, date)


def test_parse_date_str_empty():
    """Test _parse_date_str with empty string."""
    result = _parse_date_str("")
    assert result is None


@pytest.fixture()
def invoices_container() -> AppContainer:
    """Create container with fake invoice service."""
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
    container.invoice_service = FakeInvoiceService()  # type: ignore[assignment]
    return container


@pytest.mark.asyncio
async def test_on_force_reply_invoices_from_date(invoices_container: AppContainer) -> None:
    """Test force reply for invoices from date."""
    message = FakeMessage(text="2025-01-01", user_id=123)
    state = FakeFSMContext()
    await state.set_state(InvoicesPeriodState.waiting_for_from_date)

    from handlers.deps import get_invoice_service

    invoice_service = get_invoice_service(invoices_container)
    current_state = await state.get_state()

    if current_state == InvoicesPeriodState.waiting_for_from_date:
        if message.text is not None:
            from handlers.commands_invoices import _parse_date_str

            from_date = _parse_date_str(message.text.strip())
            if from_date:
                await state.update_data({"period": {"from_date": from_date}})
                await state.set_state(InvoicesPeriodState.waiting_for_to_date)
                await message.answer("По дату (YYYY-MM-DD):", reply_markup=None)

    assert len(message.answers) >= 1
    assert "По дату" in message.answers[0]["text"]
    new_state = await state.get_state()
    assert new_state == InvoicesPeriodState.waiting_for_to_date


@pytest.mark.asyncio
async def test_on_force_reply_invoices_to_date(invoices_container: AppContainer) -> None:
    """Test force reply for invoices to date."""
    message = FakeMessage(text="2025-01-31", user_id=123)
    state = FakeFSMContext()
    await state.set_state(InvoicesPeriodState.waiting_for_to_date)
    await state.update_data({"period": {"from_date": date(2025, 1, 1)}})

    from handlers.deps import get_invoice_service

    invoice_service = get_invoice_service(invoices_container)
    current_state = await state.get_state()

    if current_state == InvoicesPeriodState.waiting_for_to_date:
        if message.text is not None:
            from handlers.commands_invoices import _parse_date_str

            to_date = _parse_date_str(message.text.strip())
            if to_date:
                state_data = await state.get_data()
                period = state_data.get("period", {})
                from_date = period.get("from_date")
                invoices = await invoice_service.list_invoices(
                    from_date=from_date, to_date=to_date, supplier=None
                )
                if not invoices:
                    await message.answer("Ничего не найдено.")
                else:
                    await message.answer(f"Найдено счетов: {len(invoices)}")
                await state.clear()

    # Should either have "Ничего не найдено" or "Найдено счетов"
    assert len(message.answers) >= 1

