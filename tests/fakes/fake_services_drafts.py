from __future__ import annotations

from typing import Any, Dict, List, Optional

from backend.domain.drafts import InvoiceDraft


class FakeDraftService:
    def __init__(self) -> None:
        self.calls: List[Dict[str, Any]] = []
        self.next_draft: Optional[InvoiceDraft] = None
        self.raise_error: bool = False
        self._drafts: Dict[int, InvoiceDraft] = {}

    async def get_current_draft(self, user_id: int) -> Optional[InvoiceDraft]:
        self.calls.append({"method": "get_current_draft", "user_id": user_id})
        if self.raise_error:
            raise RuntimeError("Draft retrieval failed")
        return self._drafts.get(user_id)

    async def set_current_draft(self, user_id: int, draft: InvoiceDraft) -> None:
        self.calls.append({"method": "set_current_draft", "user_id": user_id, "draft": draft})
        if self.raise_error:
            raise RuntimeError("Draft creation failed")
        self._drafts[user_id] = draft

    async def clear_current_draft(self, user_id: int) -> None:
        self.calls.append({"method": "clear_current_draft", "user_id": user_id})
        if self.raise_error:
            raise RuntimeError("Draft deletion failed")
        self._drafts.pop(user_id, None)
