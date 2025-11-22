from __future__ import annotations

from datetime import date
from typing import Any, List, Optional, Tuple

import aiosqlite

from domain.invoices import Invoice
from storage.db import (
    DB_PATH,
    _invoice_item_to_db_row,
    _invoice_to_db_header,
    _rowset_to_invoice,
)


async def _connect() -> aiosqlite.Connection:
    """
    Open an aiosqlite connection with row factory configured for dict-like access.
    """
    connection = await aiosqlite.connect(DB_PATH)
    connection.row_factory = aiosqlite.Row
    return connection


async def save_invoice_domain_async(invoice: Invoice, user_id: int = 0) -> int:
    """
    Persist a domain Invoice into the database using aiosqlite and return the created invoice ID.
    """
    connection = await _connect()
    try:
        cursor = await connection.cursor()
        db_header = _invoice_to_db_header(invoice)
        iso = db_header.get("date_iso")

        await cursor.execute(
            """
            INSERT INTO invoices(user_id, supplier, client, doc_number, date, date_iso, total_sum, raw_text, source_path)
            VALUES(?,?,?,?,?,?,?,?,?)
            """,
            (
                user_id,
                db_header.get("supplier"),
                db_header.get("client"),
                db_header.get("doc_number"),
                db_header.get("date"),
                iso,
                db_header.get("total_sum"),
                "",
                db_header.get("source_path") or "",
            ),
        )

        invoice_id = cursor.lastrowid
        if invoice_id is None:
            await connection.close()
            return 0

        for index, item in enumerate(invoice.items, 1):
            db_item = _invoice_item_to_db_row(int(invoice_id), item, index)
            await cursor.execute(
                """
                INSERT INTO invoice_items(invoice_id, idx, code, name, qty, price, total)
                VALUES(?,?,?,?,?,?,?)
                """,
                (
                    db_item["invoice_id"],
                    db_item["idx"],
                    db_item["code"],
                    db_item["name"],
                    db_item["qty"],
                    db_item["price"],
                    db_item["total"],
                ),
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


async def fetch_invoices_domain_async(
    from_date: Optional[date],
    to_date: Optional[date],
    supplier: Optional[str] = None,
) -> List[Invoice]:
    """
    Fetch invoices from the database using aiosqlite and return them as domain Invoice entities.
    """
    connection = await _connect()
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
            invoice = _rowset_to_invoice(header_dict, item_dicts)
            invoices.append(invoice)

        return invoices
    finally:
        await connection.close()


__all__ = [
    "save_invoice_domain_async",
    "fetch_invoices_domain_async",
]
