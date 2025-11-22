from __future__ import annotations

from typing import Optional

from domain.drafts import InvoiceDraft
from storage.drafts_async import (
    delete_draft_invoice,
    load_draft_invoice,
    save_draft_invoice,
)


async def get_current_draft(user_id: int) -> Optional[InvoiceDraft]:
    """
    Retrieve the current invoice draft for the given user ID.
    """
    return await load_draft_invoice(user_id)


async def set_current_draft(user_id: int, draft: InvoiceDraft) -> None:
    """
    Persist the current invoice draft for the given user ID.
    """
    await save_draft_invoice(user_id, draft)


async def clear_current_draft(user_id: int) -> None:
    """
    Remove the current invoice draft for the given user ID.
    """
    await delete_draft_invoice(user_id)


__all__ = [
    "get_current_draft",
    "set_current_draft",
    "clear_current_draft",
]

