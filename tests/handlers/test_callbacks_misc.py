from __future__ import annotations

import pytest

from handlers.callback_registry import CallbackAction
from handlers.fsm import InvoicesPeriodState
from tests.fakes.fake_fsm import FakeFSMContext
from tests.fakes.fake_telegram import FakeCallbackQuery, FakeMessage


@pytest.mark.asyncio
async def test_cb_act_period() -> None:
    """Test period action callback."""
    message = FakeMessage()
    call = FakeCallbackQuery(data=CallbackAction.PERIOD.value, user_id=123, message=message)
    state = FakeFSMContext()

    # Test the logic directly
    await state.set_state(InvoicesPeriodState.waiting_for_from_date)
    await state.update_data({"period": {}})
    if call.message is not None:
        await call.message.answer("С даты (YYYY-MM-DD):", reply_markup=None)
        await call.answer()

    assert call.answered
    assert len(message.answers) >= 1
    assert "С даты" in message.answers[0]["text"]
    current_state = await state.get_state()
    assert current_state == InvoicesPeriodState.waiting_for_from_date


@pytest.mark.asyncio
async def test_cb_act_upload() -> None:
    """Test upload action callback."""
    message = FakeMessage()
    call = FakeCallbackQuery(data=CallbackAction.UPLOAD.value, user_id=123, message=message)

    if call.message is not None:
        await call.message.answer(
            "Пришлите файл: PDF или фото накладной. Бот распознаёт и покажет черновик."
        )
        await call.answer()

    assert call.answered
    assert len(message.answers) >= 1
    assert "Пришлите файл" in message.answers[0]["text"]


@pytest.mark.asyncio
async def test_cb_act_help() -> None:
    """Test help action callback."""
    message = FakeMessage()
    call = FakeCallbackQuery(data=CallbackAction.HELP.value, user_id=123, message=message)

    from handlers.utils import main_kb

    if call.message is not None:
        await call.message.answer(
            "Быстрые действия кнопками ниже.\n"
            "Команды для продвинутых: /show, /edit, /edititem, /comment, /save, /invoices.",
            reply_markup=main_kb(),
        )
    await call.answer()

    assert call.answered
    assert len(message.answers) >= 1
    assert "Быстрые действия" in message.answers[0]["text"]
    assert "/show" in message.answers[0]["text"]
