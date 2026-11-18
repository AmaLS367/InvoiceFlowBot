from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import List, Optional

import aiosqlite

from backend.domain.invoices import Invoice
from backend.storage.db import DB_PATH
from backend.storage.mappers import (
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
        """Initialize storage with the SQLite database path."""
        self._database_path = database_path

    async def _get_connection(self) -> aiosqlite.Connection:
        """Open an aiosqlite connection with dict-like row access."""
        Path(self._database_path).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
        connection = await aiosqlite.connect(self._database_path)
        connection.row_factory = aiosqlite.Row
        return connection

    async def save_invoice(self, invoice: Invoice, user_id: int = 0) -> int:
        """Insert invoice, items, and comments in a single transaction."""
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
        user_id: int,
        from_date: Optional[date],
        to_date: Optional[date],
        supplier: Optional[str] = None,
    ) -> List[Invoice]:
        """Fetch a user's invoices matching the date range and optional supplier filter."""
        connection = await self._get_connection()
        try:
            query = (
                "SELECT id, date, date_iso, doc_number, supplier, client, total_sum, source_path "
                "FROM invoices WHERE user_id = ?"
            )
            parameters: list[int | str] = [user_id]
            order_by = " ORDER BY created_at ASC, id ASC"
            if from_date is not None and to_date is not None:
                query += " AND date_iso BETWEEN ? AND ?"
                parameters.extend((from_date.isoformat(), to_date.isoformat()))
                order_by = " ORDER BY COALESCE(date_iso, date) ASC, id ASC"

            if supplier:
                query += " AND supplier LIKE ?"
                parameters.append(f"%{supplier}%")

            header_cursor = await connection.execute(query + order_by, parameters)
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

                comments_cursor = await connection.execute(
                    "SELECT text, user_id FROM comments WHERE invoice_id=? ORDER BY id ASC",
                    (invoice_id,),
                )
                comment_rows = await comments_cursor.fetchall()

                header_dict = dict(header_row)
                item_dicts = [dict(item_row) for item_row in item_rows]
                comment_dicts = [dict(comment_row) for comment_row in comment_rows]
                invoice = db_row_to_invoice(header_dict, item_dicts, comment_dicts)
                invoices.append(invoice)

            return invoices
        finally:
            await connection.close()


_default_storage: AsyncInvoiceStorage | None = None
_default_storage_path: str | None = None


def _get_default_storage() -> AsyncInvoiceStorage:
    """Return a cached default storage instance."""
    global _default_storage, _default_storage_path
    current_path = DB_PATH
    if _default_storage is None or _default_storage_path != current_path:
        _default_storage = AsyncInvoiceStorage(database_path=current_path)
        _default_storage_path = current_path
    return _default_storage


async def save_invoice_domain_async(invoice: Invoice, user_id: int = 0) -> int:
    """Backward compatible wrapper around AsyncInvoiceStorage.save_invoice."""
    storage = _get_default_storage()
    return await storage.save_invoice(invoice, user_id=user_id)


async def fetch_invoices_domain_async(
    user_id: int,
    from_date: Optional[date],
    to_date: Optional[date],
    supplier: Optional[str] = None,
) -> List[Invoice]:
    """Fetch a user's invoices using the default async storage."""
    storage = _get_default_storage()
    return await storage.fetch_invoices(user_id, from_date, to_date, supplier)


__all__ = [
    "AsyncInvoiceStorage",
    "save_invoice_domain_async",
    "fetch_invoices_domain_async",
]
