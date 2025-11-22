from __future__ import annotations

import types
from typing import Any, Dict

import pytest
from aiogram.types import TelegramObject

from core.container import AppContainer, create_app_container
from handlers.di_middleware import ContainerMiddleware
from ocr import async_client as real_async_client
from services import draft_service as real_draft_service
from services import invoice_service as real_invoice_service
from storage import db_async as real_db_async


def test_create_app_container_wires_real_modules() -> None:
    container = create_app_container()

    assert isinstance(container, AppContainer)

    assert container.invoice_service_module is real_invoice_service
    assert container.draft_service_module is real_draft_service
    assert container.db_async_module is real_db_async
    assert container.ocr_async_client_module is real_async_client


class FakeInvoiceService:
    def __init__(self) -> None:
        self.calls: list[Dict[str, Any]] = []

    async def process_invoice_file(self, pdf_path: str) -> str:
        self.calls.append({"pdf_path": pdf_path})
        return "fake-result"


def make_fake_container() -> AppContainer:
    fake_invoice_service = FakeInvoiceService()

    # простые заглушки для остальных полей, пока они не нужны в тесте
    fake_draft_service = types.SimpleNamespace()
    fake_db_async = types.SimpleNamespace()
    fake_ocr_client = types.SimpleNamespace()

    return AppContainer(
        invoice_service_module=fake_invoice_service,
        draft_service_module=fake_draft_service,
        db_async_module=fake_db_async,
        ocr_async_client_module=fake_ocr_client,
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

