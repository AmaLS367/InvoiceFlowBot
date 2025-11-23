"""
Fake service implementations for testing handlers.
"""

from __future__ import annotations

from datetime import date
from typing import List, Optional

from domain.invoices import Invoice


class FakeInvoiceService:
    """Fake InvoiceService for testing handlers."""

    def __init__(self) -> None:
        self.calls: List[str] = []
        self.return_invoices: List[Invoice] = []

    async def list_invoices(
        self,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        supplier: Optional[str] = None,
    ) -> List[Invoice]:
        """Fake list_invoices that records calls and returns configured invoices."""
        call_str = f"list_invoices:from_date={from_date},to_date={to_date},supplier={supplier}"
        self.calls.append(call_str)
        return self.return_invoices
