from __future__ import annotations

from typing import Any, Dict

import pytest
from aiogram.types import TelegramObject

from core.container import AppContainer
from handlers.di_middleware import ContainerMiddleware


@pytest.mark.asyncio
async def test_container_middleware_injects_container(app_container: AppContainer) -> None:
    middleware = ContainerMiddleware(container=app_container)

    called: Dict[str, Any] = {}

    async def handler(
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> None:
        called["event"] = event
        called["data"] = data

    fake_event = TelegramObject()
    initial_data: Dict[str, Any] = {}

    await middleware(
        handler=handler,
        event=fake_event,
        data=initial_data,
    )

    assert "data" in called
    data = called["data"]
    assert "container" in data
    assert data["container"] is app_container
    assert called["event"] is fake_event


@pytest.mark.asyncio
async def test_container_middleware_preserves_existing_data(app_container: AppContainer) -> None:
    middleware = ContainerMiddleware(container=app_container)

    called: Dict[str, Any] = {}

    async def handler(
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> None:
        called["data"] = data

    fake_event = TelegramObject()
    initial_data: Dict[str, Any] = {"existing_key": "existing_value"}

    await middleware(
        handler=handler,
        event=fake_event,
        data=initial_data,
    )

    data = called["data"]
    assert "container" in data
    assert data["container"] is app_container
    assert data["existing_key"] == "existing_value"
