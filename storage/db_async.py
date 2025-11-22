from __future__ import annotations

from datetime import date
from typing import List, Optional

from domain.invoices import Invoice
from services.async_utils import run_blocking_io
from storage import db as storage_db


async def save_invoice_domain_async(invoice: Invoice, user_id: int = 0) -> int:
    """
    Async wrapper for saving a domain Invoice to the database.

    This function wraps the blocking database save operation in an executor
    to allow non-blocking execution in async contexts.

    Args:
        invoice: The domain Invoice entity to save.
        user_id: Optional user ID associated with the invoice (default: 0).

    Returns:
        The database ID of the saved invoice.
    """
    invoice_id = await run_blocking_io(
        storage_db.save_invoice_domain,
        invoice,
        user_id,
    )
    return invoice_id


async def fetch_invoices_domain_async(
    from_date: Optional[date],
    to_date: Optional[date],
    supplier: Optional[str] = None,
) -> List[Invoice]:
    """
    Async wrapper for fetching invoices from the database.

    This function wraps the blocking database fetch operation in an executor
    to allow non-blocking execution in async contexts.

    Args:
        from_date: Optional start date for filtering invoices.
        to_date: Optional end date for filtering invoices.
        supplier: Optional supplier name filter (partial match).

    Returns:
        List of Invoice domain entities matching the criteria.
    """
    invoices = await run_blocking_io(
        storage_db.fetch_invoices_domain,
        from_date,
        to_date,
        supplier,
    )
    return invoices


__all__ = [
    "save_invoice_domain_async",
    "fetch_invoices_domain_async",
]

