from __future__ import annotations

import logging
from typing import Awaitable, Callable, Optional

from domain.drafts import InvoiceDraft


class DraftService:
    def __init__(
        self,
        load_draft_func: Callable[[int], Awaitable[Optional[InvoiceDraft]]],
        save_draft_func: Callable[[int, InvoiceDraft], Awaitable[None]],
        delete_draft_func: Callable[[int], Awaitable[None]],
        logger: logging.Logger,
    ) -> None:
        self._load_draft_func = load_draft_func
        self._save_draft_func = save_draft_func
        self._delete_draft_func = delete_draft_func
        self._logger = logger

    async def get_current_draft(self, user_id: int) -> Optional[InvoiceDraft]:
        return await self._load_draft_func(user_id)

    async def set_current_draft(self, user_id: int, draft: InvoiceDraft) -> None:
        await self._save_draft_func(user_id, draft)

    async def clear_current_draft(self, user_id: int) -> None:
        await self._delete_draft_func(user_id)


__all__ = [
    "DraftService",
]
