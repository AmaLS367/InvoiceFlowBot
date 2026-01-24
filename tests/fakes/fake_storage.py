from __future__ import annotations

from datetime import date
from typing import Any, List, Optional

from backend.domain.drafts import InvoiceDraft
from backend.domain.invoices import Invoice


class FakeStorage:
    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple[Any, ...], dict[str, Any]]] = []
        self._saved_invoices: dict[int, Invoice] = {}
        self._saved_drafts: dict[int, InvoiceDraft] = {}
        self._next_invoice_id = 1

    async def save_invoice_domain_async(self, invoice: Invoice, user_id: int = 0) -> int:
        """Fake save invoice function."""
        self.calls.append(("save_invoice_domain_async", (invoice, user_id), {}))
        invoice_id = self._next_invoice_id
        self._next_invoice_id += 1
        self._saved_invoices[invoice_id] = invoice
        return invoice_id

    async def fetch_invoices_domain_async(
        self,
        from_date: Optional[date],
        to_date: Optional[date],
        supplier: Optional[str] = None,
    ) -> List[Invoice]:
        """Fake fetch invoices function."""
        self.calls.append(("fetch_invoices_domain_async", (from_date, to_date, supplier), {}))
        return list(self._saved_invoices.values())

    async def load_draft_invoice(self, user_id: int) -> Optional[InvoiceDraft]:
        """Fake load draft function."""
        self.calls.append(("load_draft_invoice", (user_id,), {}))
        return self._saved_drafts.get(user_id)

    async def save_draft_invoice(self, user_id: int, draft: InvoiceDraft) -> None:
        """Fake save draft function."""
        self.calls.append(("save_draft_invoice", (user_id, draft), {}))
        self._saved_drafts[user_id] = draft

    async def delete_draft_invoice(self, user_id: int) -> None:
        """Fake delete draft function."""
        self.calls.append(("delete_draft_invoice", (user_id,), {}))
        self._saved_drafts.pop(user_id, None)


def make_fake_save_invoice_func(fake_storage: FakeStorage) -> Any:
    """Create a callable that delegates to fake_storage.save_invoice_domain_async."""

    async def fake_save_invoice(invoice: Invoice, user_id: int = 0) -> int:
        return await fake_storage.save_invoice_domain_async(invoice, user_id)

    return fake_save_invoice


def make_fake_fetch_invoices_func(fake_storage: FakeStorage) -> Any:
    """Create a callable that delegates to fake_storage.fetch_invoices_domain_async."""

    async def fake_fetch_invoices(
        from_date: Optional[date],
        to_date: Optional[date],
        supplier: Optional[str] = None,
    ) -> List[Invoice]:
        return await fake_storage.fetch_invoices_domain_async(from_date, to_date, supplier)

    return fake_fetch_invoices


def make_fake_load_draft_func(fake_storage: FakeStorage) -> Any:
    """Create a callable that delegates to fake_storage.load_draft_invoice."""

    async def fake_load_draft(user_id: int) -> Optional[InvoiceDraft]:
        return await fake_storage.load_draft_invoice(user_id)

    return fake_load_draft


def make_fake_save_draft_func(fake_storage: FakeStorage) -> Any:
    """Create a callable that delegates to fake_storage.save_draft_invoice."""

    async def fake_save_draft(user_id: int, draft: InvoiceDraft) -> None:
        await fake_storage.save_draft_invoice(user_id, draft)

    return fake_save_draft


def make_fake_delete_draft_func(fake_storage: FakeStorage) -> Any:
    """Create a callable that delegates to fake_storage.delete_draft_invoice."""

    async def fake_delete_draft(user_id: int) -> None:
        await fake_storage.delete_draft_invoice(user_id)

    return fake_delete_draft


__all__ = [
    "FakeStorage",
    "make_fake_save_invoice_func",
    "make_fake_fetch_invoices_func",
    "make_fake_load_draft_func",
    "make_fake_save_draft_func",
    "make_fake_delete_draft_func",
]
