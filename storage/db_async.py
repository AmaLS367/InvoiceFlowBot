"""
Async data access layer built on top of aiosqlite.

Provides high-level operations for reading and writing invoice-related data.
All SQL logic is centralized in the AsyncInvoiceStorage class.
"""
from __future__ import annotations

from datetime import date
from typing import Any, List, Optional, Tuple

import aiosqlite

from domain.invoices import Invoice
from storage.db import DB_PATH
from storage.mappers import (
    db_row_to_invoice,
    invoice_item_to_db_row,
    invoice_to_db_row,
)


class AsyncInvoiceStorage:
    """
    Async storage for invoice-related data.

    This is the single source of truth for all SQL operations on invoices.
    """

    def __init__(self, database_path: str) -> None:
        """
        Initialize storage with the database path.

        Args:
            database_path: Path to the SQLite database file.
        """
        self._database_path = database_path

    async def _get_connection(self) -> aiosqlite.Connection:
        """
        Open an aiosqlite connection with row factory configured for dict-like access.
        """
        connection = await aiosqlite.connect(self._database_path)
        connection.row_factory = aiosqlite.Row
        return connection

    async def save_invoice(self, invoice: Invoice, user_id: int = 0) -> int:
        """
        Insert invoice and related items in a single transaction, return the created invoice ID.

        Args:
            invoice: Domain Invoice entity to persist.
            user_id: User ID associated with the invoice.

        Returns:
            The created invoice ID, or 0 if insertion failed.
        """
        connection = await self._get_connection()
        try:
            cursor = await connection.cursor()
            db_row = invoice_to_db_row(invoice, user_id=user_id)

            await cursor.execute(
                """
                INSERT INTO invoices(user_id, supplier, client, doc_number, date, date_iso, total_sum, raw_text, source_path)
                VALUES(:user_id, :supplier, :client, :doc_number, :date, :date_iso, :total_sum, :raw_text, :source_path)
                """,
                db_row,
            )

            invoice_id = cursor.lastrowid
            if invoice_id is None:
                await connection.close()
                return 0

            for index, item in enumerate(invoice.items, 1):
                item_row = invoice_item_to_db_row(int(invoice_id), item, index)
                await cursor.execute(
                    """
                    INSERT INTO invoice_items(invoice_id, idx, code, name, qty, price, total)
                    VALUES(:invoice_id, :idx, :code, :name, :qty, :price, :total)
                    """,
                    item_row,
                )

            for comment in invoice.comments:
                comment_user_id = user_id
                if comment.author:
                    try:
                        comment_user_id = int(comment.author)
                    except (ValueError, TypeError):
                        pass
                await cursor.execute(
                    "INSERT INTO comments(invoice_id, user_id, text) VALUES(?,?,?)",
                    (invoice_id, comment_user_id, comment.message),
                )

            await connection.commit()
            return int(invoice_id or 0)
        finally:
            await connection.close()

    async def fetch_invoices(
        self,
        from_date: Optional[date],
        to_date: Optional[date],
        supplier: Optional[str] = None,
    ) -> List[Invoice]:
        """
        Fetch invoices matching the date range and optional supplier filter.

        Results are sorted by date (or creation time if dates are missing).

        Args:
            from_date: Start date for filtering (inclusive).
            to_date: End date for filtering (inclusive).
            supplier: Optional supplier name filter (LIKE pattern).

        Returns:
            List of Invoice domain entities.
        """
        connection = await self._get_connection()
        try:
            from_iso = from_date.isoformat() if from_date else None
            to_iso = to_date.isoformat() if to_date else None

            if from_iso and to_iso:
                if supplier:
                    query = (
                        "SELECT id, date, date_iso, doc_number, supplier, client, total_sum, source_path "
                        "FROM invoices "
                        "WHERE COALESCE(date_iso, date) IS NOT NULL "
                        "AND date_iso BETWEEN ? AND ? AND supplier LIKE ? "
                        "ORDER BY COALESCE(date_iso, date) ASC, id ASC"
                    )
                    parameters: Tuple[Any, ...] = (from_iso, to_iso, f"%{supplier}%")
                else:
                    query = (
                        "SELECT id, date, date_iso, doc_number, supplier, client, total_sum, source_path "
                        "FROM invoices "
                        "WHERE COALESCE(date_iso, date) IS NOT NULL "
                        "AND date_iso BETWEEN ? AND ? "
                        "ORDER BY COALESCE(date_iso, date) ASC, id ASC"
                    )
                    parameters = (from_iso, to_iso)
            else:
                if supplier:
                    query = (
                        "SELECT id, date, date_iso, doc_number, supplier, client, total_sum, source_path "
                        "FROM invoices "
                        "WHERE supplier LIKE ? "
                        "ORDER BY created_at ASC, id ASC"
                    )
                    parameters = (f"%{supplier}%",)
                else:
                    query = (
                        "SELECT id, date, date_iso, doc_number, supplier, client, total_sum, source_path "
                        "FROM invoices "
                        "ORDER BY created_at ASC, id ASC"
                    )
                    parameters = ()

            header_cursor = await connection.execute(query, parameters)
            header_rows = await header_cursor.fetchall()

            invoices: List[Invoice] = []
            for header_row in header_rows:
                invoice_id = header_row["id"]
                items_cursor = await connection.execute(
                    "SELECT code, name, qty, price, total "
                    "FROM invoice_items "
                    "WHERE invoice_id=? ORDER BY idx ASC",
                    (invoice_id,),
                )
                item_rows = await items_cursor.fetchall()

                header_dict = dict(header_row)
                item_dicts = [dict(item_row) for item_row in item_rows]
                invoice = db_row_to_invoice(header_dict, item_dicts)
                invoices.append(invoice)

            return invoices
        finally:
            await connection.close()


# Default storage instance for backward compatibility
# Note: This uses DB_PATH from storage.db, which may be monkeypatched in tests
_default_storage: AsyncInvoiceStorage | None = None
_default_storage_path: str | None = None


def _get_default_storage() -> AsyncInvoiceStorage:
    """Get or create the default storage instance."""
    global _default_storage, _default_storage_path
    # Recreate storage if DB_PATH changed (e.g., in tests)
    current_path = DB_PATH
    if _default_storage is None or _default_storage_path != current_path:
        _default_storage = AsyncInvoiceStorage(database_path=current_path)
        _default_storage_path = current_path
    return _default_storage


# Wrapper functions for backward compatibility
async def save_invoice_domain_async(invoice: Invoice, user_id: int = 0) -> int:
    """
    Save invoice domain entity to database (backward compatibility wrapper).

    This function delegates to AsyncInvoiceStorage.save_invoice.
    """
    storage = _get_default_storage()
    return await storage.save_invoice(invoice, user_id=user_id)


async def fetch_invoices_domain_async(
    from_date: Optional[date],
    to_date: Optional[date],
    supplier: Optional[str] = None,
) -> List[Invoice]:
    """
    Fetch invoices from database (backward compatibility wrapper).

    This function delegates to AsyncInvoiceStorage.fetch_invoices.
    """
    storage = _get_default_storage()
    return await storage.fetch_invoices(from_date=from_date, to_date=to_date, supplier=supplier)


__all__ = [
    "AsyncInvoiceStorage",
    "save_invoice_domain_async",
    "fetch_invoices_domain_async",
]
