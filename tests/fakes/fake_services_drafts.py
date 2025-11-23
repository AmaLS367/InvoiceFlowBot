"""
Fake DraftService for testing handlers.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from domain.drafts import InvoiceDraft


class FakeDraftService:
    """Fake DraftService for testing handlers."""

    def __init__(self) -> None:
        self.calls: List[Dict[str, Any]] = []
        self.next_draft: Optional[InvoiceDraft] = None
        self._drafts: Dict[int, InvoiceDraft] = {}

    async def get_current_draft(self, user_id: int) -> Optional[InvoiceDraft]:
        """Fake get_current_draft that records calls."""
        self.calls.append({"method": "get_current_draft", "user_id": user_id})
        return self._drafts.get(user_id)

    async def set_current_draft(self, user_id: int, draft: InvoiceDraft) -> None:
        """Fake set_current_draft that records calls."""
        self.calls.append({"method": "set_current_draft", "user_id": user_id, "draft": draft})
        self._drafts[user_id] = draft

    async def clear_current_draft(self, user_id: int) -> None:
        """Fake clear_current_draft that records calls."""
        self.calls.append({"method": "clear_current_draft", "user_id": user_id})
        self._drafts.pop(user_id, None)

