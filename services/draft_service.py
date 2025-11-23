"""
Business logic for managing per-user invoice drafts.

Drafts represent the in-progress state of a parsed invoice.
"""
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
        """
        Retrieve the current invoice draft for the given user ID.
        """
        return await self._load_draft_func(user_id)

    async def set_current_draft(self, user_id: int, draft: InvoiceDraft) -> None:
        """
        Persist the current invoice draft for the given user ID.
        """
        await self._save_draft_func(user_id, draft)

    async def clear_current_draft(self, user_id: int) -> None:
        """
        Remove the current invoice draft for the given user ID.
        """
        await self._delete_draft_func(user_id)


__all__ = [
    "DraftService",
]

