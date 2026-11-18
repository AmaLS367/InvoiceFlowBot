from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from backend.handlers import texts
from backend.storage.user_languages import UserLanguageStorage


class LocaleMiddleware(BaseMiddleware):
    """Resolve the locale once per update and scope it to that update's task."""

    def __init__(self, storage: UserLanguageStorage) -> None:
        self._storage = storage

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        preferred = await self._storage.get(user.id) if user else None
        locale = texts.resolve_locale(preferred, user.language_code if user else None)
        data["language_storage"] = self._storage
        data["preferred_language"] = preferred
        with texts.use_locale(locale):
            return await handler(event, data)
