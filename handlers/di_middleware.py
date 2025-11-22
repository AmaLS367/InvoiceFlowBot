from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from core.container import AppContainer


class ContainerMiddleware(BaseMiddleware):
    """
    Aiogram middleware that injects the AppContainer into handler data.

    Handlers can then declare a `container: AppContainer` argument
    to receive the current dependency container.
    """

    def __init__(self, container: AppContainer) -> None:
        super().__init__()
        self._container = container

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        data["container"] = self._container
        return await handler(event, data)


__all__ = ["ContainerMiddleware"]

