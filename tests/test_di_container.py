from __future__ import annotations

import types
from typing import Any, Dict

import pytest
from aiogram.types import TelegramObject

from core.container import AppContainer, create_app_container
from handlers.di_middleware import ContainerMiddleware
from services.draft_service import DraftService
from services.invoice_service import InvoiceService


def test_create_app_container_wires_real_services() -> None:
    container = create_app_container()

    assert isinstance(container, AppContainer)

    assert isinstance(container.invoice_service, InvoiceService)
    assert isinstance(container.draft_service, DraftService)
    assert container.invoice_service_module is container.invoice_service
    assert container.draft_service_module is container.draft_service


class FakeInvoiceService:
    def __init__(self) -> None:
        self.calls: list[Dict[str, Any]] = []

    async def process_invoice_file(self, pdf_path: str) -> str:
        self.calls.append({"pdf_path": pdf_path})
        return "fake-result"


def make_fake_container() -> AppContainer:
    fake_invoice_service = FakeInvoiceService()

    fake_draft_service = types.SimpleNamespace()

    return AppContainer(
        invoice_service=fake_invoice_service,
        draft_service=fake_draft_service,
    )


async def fake_handler(event: TelegramObject, data: Dict[str, Any]) -> str:
    container = data["container"]
    result: str = await container.invoice_service_module.process_invoice_file("tests/data/sample.pdf")
    return result


@pytest.mark.asyncio
async def test_container_middleware_injects_container_and_calls_fake_service() -> None:
    fake_container = make_fake_container()
    middleware = ContainerMiddleware(fake_container)

    event = TelegramObject()
    data: Dict[str, Any] = {}

    result = await middleware(
        handler=fake_handler,
        event=event,
        data=data,
    )

    assert result == "fake-result"

    invoice_service = fake_container.invoice_service_module
    assert isinstance(invoice_service, FakeInvoiceService)
    assert len(invoice_service.calls) == 1
    assert invoice_service.calls[0]["pdf_path"] == "tests/data/sample.pdf"

