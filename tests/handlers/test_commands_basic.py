from __future__ import annotations

import pytest

from core.container import AppContainer
from handlers.commands_common import cmd_help, cmd_start
from handlers.commands_invoices import cmd_invoices
from tests.fakes.fake_services import FakeInvoiceService
from tests.fakes.fake_telegram import FakeMessage


@pytest.mark.asyncio
async def test_cmd_start_sends_welcome_message(
    app_container: AppContainer,
) -> None:
    message = FakeMessage(text="/start")

    await cmd_start(message)

    assert len(message.answers) >= 1

    first_answer = message.answers[0]["text"]
    assert isinstance(first_answer, str)
    assert first_answer != ""
    assert "инвойсов" in first_answer or "счет" in first_answer or "бот" in first_answer


@pytest.mark.asyncio
async def test_cmd_help_sends_help_message(
    app_container: AppContainer,
) -> None:
    message = FakeMessage(text="/help")

    await cmd_help(message)

    assert len(message.answers) >= 1

    first_answer = message.answers[0]["text"]
    assert isinstance(first_answer, str)
    assert first_answer != ""
    assert "команды" in first_answer.lower() or "commands" in first_answer.lower()


@pytest.mark.asyncio
async def test_cmd_invoices_uses_service_and_answers(
    handlers_container: AppContainer,
    fake_invoice_service: FakeInvoiceService,
) -> None:
    message = FakeMessage(text="/invoices 2025-01-01 2025-01-31")

    await cmd_invoices(message, handlers_container)

    assert len(fake_invoice_service.calls) >= 1
    assert any("list_invoices" in call for call in fake_invoice_service.calls)

    assert len(message.answers) >= 1
    first_answer = message.answers[0]["text"]
    assert isinstance(first_answer, str)
    assert first_answer != ""


@pytest.mark.asyncio
async def test_cmd_invoices_with_supplier_filter(
    handlers_container: AppContainer,
    fake_invoice_service: FakeInvoiceService,
) -> None:
    message = FakeMessage(text="/invoices 2025-01-01 2025-01-31 supplier=TestSupplier")

    await cmd_invoices(message, handlers_container)

    assert len(fake_invoice_service.calls) >= 1
    assert any("supplier=TestSupplier" in call for call in fake_invoice_service.calls)

    assert len(message.answers) >= 1


@pytest.mark.asyncio
async def test_cmd_invoices_handles_invalid_format(
    app_container: AppContainer,
) -> None:
    message = FakeMessage(text="/invoices invalid")

    await cmd_invoices(message, app_container)

    assert len(message.answers) >= 1
    first_answer = message.answers[0]["text"]
    assert "Формат" in first_answer or "формат" in first_answer.lower()
