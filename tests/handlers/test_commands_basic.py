"""
Basic tests for command handlers: /start, /help, /invoices.
"""
from __future__ import annotations

from typing import Any, Dict

import pytest

from handlers.commands_common import cmd_help, cmd_start
from handlers.commands_invoices import cmd_invoices
from tests.fakes.fake_services import FakeInvoiceService
from tests.fakes.fake_telegram import FakeMessage


@pytest.mark.asyncio
async def test_cmd_start_sends_welcome_message(
    handlers_data: Dict[str, Any],
) -> None:
    """Test that /start command sends a welcome message."""
    message = FakeMessage(text="/start")

    await cmd_start(message, handlers_data)

    assert len(message.answers) >= 1

    first_answer = message.answers[0]["text"]
    assert isinstance(first_answer, str)
    assert first_answer != ""
    # Check that message contains expected content
    assert "накладной" in first_answer or "PDF" in first_answer or "файл" in first_answer


@pytest.mark.asyncio
async def test_cmd_help_sends_help_message(
    handlers_data: Dict[str, Any],
) -> None:
    """Test that /help command sends a help message."""
    message = FakeMessage(text="/help")

    await cmd_help(message, handlers_data)

    assert len(message.answers) >= 1

    first_answer = message.answers[0]["text"]
    assert isinstance(first_answer, str)
    assert first_answer != ""
    # Check that message contains expected content
    assert "команды" in first_answer.lower() or "commands" in first_answer.lower()


@pytest.mark.asyncio
async def test_cmd_invoices_uses_service_and_answers(
    handlers_data: Dict[str, Any],
    fake_invoice_service: FakeInvoiceService,
) -> None:
    """Test that /invoices command uses InvoiceService and sends response."""
    message = FakeMessage(text="/invoices 2025-01-01 2025-01-31")

    await cmd_invoices(message, handlers_data)

    # Verify service was called
    assert len(fake_invoice_service.calls) >= 1
    assert any("list_invoices" in call for call in fake_invoice_service.calls)

    # Verify message was sent
    assert len(message.answers) >= 1
    first_answer = message.answers[0]["text"]
    assert isinstance(first_answer, str)
    assert first_answer != ""


@pytest.mark.asyncio
async def test_cmd_invoices_with_supplier_filter(
    handlers_data: Dict[str, Any],
    fake_invoice_service: FakeInvoiceService,
) -> None:
    """Test that /invoices command handles supplier filter parameter."""
    message = FakeMessage(text="/invoices 2025-01-01 2025-01-31 supplier=TestSupplier")

    await cmd_invoices(message, handlers_data)

    # Verify service was called with supplier
    assert len(fake_invoice_service.calls) >= 1
    assert any("supplier=TestSupplier" in call for call in fake_invoice_service.calls)

    # Verify message was sent
    assert len(message.answers) >= 1


@pytest.mark.asyncio
async def test_cmd_invoices_handles_invalid_format(
    handlers_data: Dict[str, Any],
) -> None:
    """Test that /invoices command handles invalid format gracefully."""
    message = FakeMessage(text="/invoices invalid")

    await cmd_invoices(message, handlers_data)

    # Should send error message about format
    assert len(message.answers) >= 1
    first_answer = message.answers[0]["text"]
    assert "Формат" in first_answer or "формат" in first_answer.lower()

