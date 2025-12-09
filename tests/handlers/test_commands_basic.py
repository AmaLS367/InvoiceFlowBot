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


@pytest.mark.asyncio
async def test_cmd_invoices_with_no_text(
    app_container: AppContainer,
) -> None:
    """Test /invoices command with None text."""
    message = FakeMessage(text=None)  # type: ignore[arg-type]

    await cmd_invoices(message, app_container)

    assert len(message.answers) >= 1
    assert "Формат" in message.answers[0]["text"]


@pytest.mark.asyncio
async def test_cmd_invoices_no_results(
    handlers_container: AppContainer,
    fake_invoice_service: FakeInvoiceService,
) -> None:
    """Test /invoices command when no invoices found."""
    fake_invoice_service.return_invoices = []
    message = FakeMessage(text="/invoices 2025-01-01 2025-01-31")

    await cmd_invoices(message, handlers_container)

    assert len(message.answers) >= 1
    assert "Ничего не найдено" in message.answers[0]["text"]


@pytest.mark.asyncio
async def test_cmd_invoices_with_results(
    handlers_container: AppContainer,
    fake_invoice_service: FakeInvoiceService,
) -> None:
    """Test /invoices command with results."""
    from datetime import date
    from decimal import Decimal

    from domain.invoices import Invoice, InvoiceHeader, InvoiceItem

    invoice = Invoice(
        header=InvoiceHeader(
            supplier_name="Test Supplier",
            invoice_number="INV-001",
            invoice_date=date(2025, 1, 15),
            total_amount=Decimal("100.00"),
        ),
        items=[
            InvoiceItem(
                description="Item 1",
                quantity=Decimal("1"),
                unit_price=Decimal("100.00"),
                line_total=Decimal("100.00"),
            ),
        ],
    )
    fake_invoice_service.return_invoices = [invoice]
    message = FakeMessage(text="/invoices 2025-01-01 2025-01-31")

    await cmd_invoices(message, handlers_container)

    assert len(message.answers) >= 1
    answer_text = message.answers[0]["text"]
    assert "Счета с" in answer_text
    assert "Test Supplier" in answer_text
    assert "100" in answer_text
