from __future__ import annotations

from datetime import date
from typing import List, Optional

from domain.invoices import Invoice


class FakeInvoiceService:
    def __init__(self) -> None:
        self.calls: List[str] = []
        self.return_invoices: List[Invoice] = []

    async def list_invoices(
        self,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        supplier: Optional[str] = None,
    ) -> List[Invoice]:
        call_str = f"list_invoices:from_date={from_date},to_date={to_date},supplier={supplier}"
        self.calls.append(call_str)
        return self.return_invoices

    async def save_invoice(self, invoice: Invoice, user_id: int = 0) -> int:
        call_str = f"save_invoice:user_id={user_id},invoice={invoice.header.invoice_number}"
        self.calls.append(call_str)
        return 123  # Return fake invoice ID
