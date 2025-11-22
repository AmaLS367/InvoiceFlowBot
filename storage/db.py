from __future__ import annotations

import os
import re
import sqlite3
from datetime import date
from decimal import Decimal
from typing import Any, Dict, List, Optional, cast

from domain.invoices import (
    Invoice,
    InvoiceHeader,
    InvoiceItem,
    InvoiceSourceInfo,
)

DB_PATH = os.getenv("INVOICE_DB_PATH", "data.sqlite")

def _conn():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    con = _conn()
    cur = con.cursor()
    cur.executescript("""
    PRAGMA journal_mode=WAL;
    CREATE TABLE IF NOT EXISTS invoices(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        supplier TEXT,
        client TEXT,
        doc_number TEXT,
        date TEXT,
        date_iso TEXT,               -- YYYY-MM-DD if parsed successfully
        total_sum REAL,
        raw_text TEXT,
        source_path TEXT,
        created_at TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS invoice_items(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_id INTEGER NOT NULL,
        idx INTEGER NOT NULL,
        code TEXT,
        name TEXT,
        qty REAL,
        price REAL,
        total REAL,
        FOREIGN KEY(invoice_id) REFERENCES invoices(id) ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS comments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        text TEXT NOT NULL,
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY(invoice_id) REFERENCES invoices(id) ON DELETE CASCADE
    );
    """)
    con.commit()
    con.close()

_MONTHS = {
    # Russian
    "января":1,"февраля":2,"марта":3,"апреля":4,"мая":5,"июня":6,"июля":7,"августа":8,"сентября":9,"октября":10,"ноября":11,"декабря":12,
    # English
    "january":1,"february":2,"march":3,"april":4,"may":5,"june":6,"july":7,"august":8,"september":9,"october":10,"november":11,"december":12,
    # French
    "janvier":1,"février":2,"fevrier":2,"mars":3,"avril":4,"mai":5,"juin":6,"juillet":7,"août":8,"aout":8,"septembre":9,"octobre":10,"novembre":11,"décembre":12,"decembre":12,
}

def to_iso(d: Optional[str]) -> Optional[str]:
    """
    Convert date string to ISO format (YYYY-MM-DD).
    Supports various date formats including numeric and locale-specific formats.
    """
    if not d:
        return None
    s = d.strip()
    s = re.sub(r"[ \u00A0\u202f]+", " ", s)
    # 1) 2025-06-12 or 12/06/2025, 12-06-25, 12.06.2025
    m = re.match(r"^(\d{4})[./-](\d{1,2})[./-](\d{1,2})$", s)
    if m:
        y, mo, da = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return f"{y:04d}-{mo:02d}-{da:02d}"
    m = re.match(r"^(\d{1,2})[./-](\d{1,2})[./-](\d{2,4})$", s)
    if m:
        da, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if y < 100:
            y += 2000 if y <= 68 else 1900
        return f"{y:04d}-{mo:02d}-{da:02d}"
    # 2) 12 June 2025 / 12 juin 2025
    m = re.match(r"^(\d{1,2})\s+([A-Za-z\u00E9\u00EA\u00FB\u00EE\u00F4\u00E8\u00E0\u00F9\u00EF\u00EB\u00E7]+)\s+(\d{2,4})$", s, flags=re.I)
    if m:
        da = int(m.group(1))
        mon = m.group(2).lower()
        y = int(m.group(3))
        if y < 100:
            y += 2000 if y <= 68 else 1900
        month_num = _MONTHS.get(mon)
        if month_num is not None:
            return f"{y:04d}-{month_num:02d}-{da:02d}"
    return None

def save_invoice(user_id: int, parsed: Dict[str, Any], source_path: str, raw_text: Optional[str] = None, comments: Optional[List[str]] = None) -> int:
    con = _conn()
    cur = con.cursor()
    iso = to_iso(parsed.get("date"))
    cur.execute("""
        INSERT INTO invoices(user_id, supplier, client, doc_number, date, date_iso, total_sum, raw_text, source_path)
        VALUES(?,?,?,?,?,?,?,?,?)
    """, (
        user_id,
        parsed.get("supplier"),
        parsed.get("client"),
        parsed.get("doc_number"),
        parsed.get("date"),
        iso,
        parsed.get("total_sum"),
        raw_text or "",
        source_path,
    ))
    invoice_id = cur.lastrowid
    for i, it in enumerate(parsed.get("items") or [], 1):
        cur.execute("""
            INSERT INTO invoice_items(invoice_id, idx, code, name, qty, price, total)
            VALUES(?,?,?,?,?,?,?)
        """, (invoice_id, i, it.get("code") or "", it.get("name") or "", float(it.get("qty") or 0), float(it.get("price") or 0), float(it.get("total") or 0)))
    for text in (comments or []):
        cur.execute("INSERT INTO comments(invoice_id, user_id, text) VALUES(?,?,?)", (invoice_id, user_id, text))
    con.commit()
    con.close()
    return int(invoice_id or 0)

def add_comment(invoice_id: int, user_id: int, text: str) -> None:
    con = _conn()
    con.execute("INSERT INTO comments(invoice_id, user_id, text) VALUES(?,?,?)", (invoice_id, user_id, text))
    con.commit()
    con.close()

def query_invoices(user_id: int, date_from: str, date_to: str, supplier: Optional[str] = None) -> List[sqlite3.Row]:
    f_iso, t_iso = to_iso(date_from), to_iso(date_to)
    con = _conn()
    if f_iso and t_iso:
        if supplier:
            rows = con.execute(
                "SELECT id, date, date_iso, doc_number, supplier, client, total_sum FROM invoices "
                "WHERE user_id=? AND COALESCE(date_iso, date) IS NOT NULL "
                "AND date_iso BETWEEN ? AND ? AND supplier LIKE ? "
                "ORDER BY COALESCE(date_iso, date) ASC, id ASC",
                (user_id, f_iso, t_iso, f"%{supplier}%")
            ).fetchall()
        else:
            rows = con.execute(
                "SELECT id, date, date_iso, doc_number, supplier, client, total_sum FROM invoices "
                "WHERE user_id=? AND COALESCE(date_iso, date) IS NOT NULL "
                "AND date_iso BETWEEN ? AND ? "
                "ORDER BY COALESCE(date_iso, date) ASC, id ASC",
                (user_id, f_iso, t_iso)
            ).fetchall()
    else:
        # If ISO parsing failed, search by created_at
        if supplier:
            rows = con.execute(
                "SELECT id, date, date_iso, doc_number, supplier, client, total_sum FROM invoices "
                "WHERE user_id=? AND created_at BETWEEN ? AND datetime(?, '+1 day') AND supplier LIKE ? "
                "ORDER BY created_at ASC, id ASC",
                (user_id, date_from, date_to, f"%{supplier}%")
            ).fetchall()
        else:
            rows = con.execute(
                "SELECT id, date, date_iso, doc_number, supplier, client, total_sum FROM invoices "
                "WHERE user_id=? AND created_at BETWEEN ? AND datetime(?, '+1 day') "
                "ORDER BY created_at ASC, id ASC",
                (user_id, date_from, date_to)
            ).fetchall()
    con.close()
    return cast(List[sqlite3.Row], rows)

def items_count(invoice_id: int) -> int:
    con = _conn()
    n = con.execute("SELECT COUNT(1) FROM invoice_items WHERE invoice_id=?", (invoice_id,)).fetchone()[0]
    con.close()
    return int(n)


def _invoice_to_db_header(invoice: Invoice) -> dict:
    """
    Convert domain Invoice header to a dict suitable for inserting into the invoices table.
    """
    header = invoice.header
    date_iso = None
    if header.invoice_date:
        date_iso = header.invoice_date.isoformat()

    source_path = None
    if invoice.source and invoice.source.file_path:
        source_path = invoice.source.file_path

    total_sum = None
    if header.total_amount is not None:
        total_sum = float(header.total_amount)

    return {
        "supplier": header.supplier_name,
        "client": header.customer_name,
        "doc_number": header.invoice_number,
        "date": header.invoice_date.isoformat() if header.invoice_date else None,
        "date_iso": date_iso,
        "total_sum": total_sum,
        "source_path": source_path,
    }


def _invoice_item_to_db_row(invoice_id: int, item: InvoiceItem, index: int) -> dict:
    """
    Convert a single InvoiceItem to a dict suitable for inserting into the invoice_items table.
    """
    return {
        "invoice_id": invoice_id,
        "idx": index,
        "code": item.sku or "",
        "name": item.description or "",
        "qty": float(item.quantity),
        "price": float(item.unit_price),
        "total": float(item.line_total),
    }


def _rowset_to_invoice(
    header_row: dict,
    item_rows: List[dict],
) -> Invoice:
    """
    Build a domain Invoice entity from a database header row and related item rows.
    """
    invoice_date = None
    if header_row.get("date_iso"):
        try:
            invoice_date = date.fromisoformat(header_row["date_iso"])
        except (ValueError, TypeError):
            pass

    total_amount = None
    if header_row.get("total_sum") is not None:
        total_amount = Decimal(str(header_row["total_sum"]))

    header = InvoiceHeader(
        supplier_name=header_row.get("supplier"),
        customer_name=header_row.get("client"),
        invoice_number=header_row.get("doc_number"),
        invoice_date=invoice_date,
        total_amount=total_amount,
    )

    items = []
    for item_row in item_rows:
        item = InvoiceItem(
            description=item_row.get("name") or "",
            sku=item_row.get("code"),
            quantity=Decimal(str(item_row.get("qty", 0))),
            unit_price=Decimal(str(item_row.get("price", 0))),
            line_total=Decimal(str(item_row.get("total", 0))),
        )
        items.append(item)

    source = InvoiceSourceInfo(
        file_path=header_row.get("source_path"),
        file_sha256=None,
        provider=None,
        raw_payload_path=None,
    )

    invoice = Invoice(
        header=header,
        items=items,
        comments=[],
        source=source,
    )

    return invoice


def save_invoice_domain(invoice: Invoice, user_id: int = 0) -> int:
    """
    Persist a domain Invoice into the database and return the created invoice ID.
    """
    con = _conn()
    cur = con.cursor()

    db_header = _invoice_to_db_header(invoice)
    iso = db_header.get("date_iso")

    cur.execute("""
        INSERT INTO invoices(user_id, supplier, client, doc_number, date, date_iso, total_sum, raw_text, source_path)
        VALUES(?,?,?,?,?,?,?,?,?)
    """, (
        user_id,
        db_header.get("supplier"),
        db_header.get("client"),
        db_header.get("doc_number"),
        db_header.get("date"),
        iso,
        db_header.get("total_sum"),
        "",
        db_header.get("source_path") or "",
    ))

    invoice_id = cur.lastrowid
    if invoice_id is None:
        con.close()
        return 0

    for index, item in enumerate(invoice.items, 1):
        db_item = _invoice_item_to_db_row(invoice_id, item, index)
        cur.execute("""
            INSERT INTO invoice_items(invoice_id, idx, code, name, qty, price, total)
            VALUES(?,?,?,?,?,?,?)
        """, (
            db_item["invoice_id"],
            db_item["idx"],
            db_item["code"],
            db_item["name"],
            db_item["qty"],
            db_item["price"],
            db_item["total"],
        ))

    for comment in invoice.comments:
        comment_user_id = user_id
        if comment.author:
            try:
                comment_user_id = int(comment.author)
            except (ValueError, TypeError):
                pass
        cur.execute(
            "INSERT INTO comments(invoice_id, user_id, text) VALUES(?,?,?)",
            (invoice_id, comment_user_id, comment.message)
        )

    con.commit()
    con.close()
    return int(invoice_id or 0)


def fetch_invoices_domain(
    from_date: Optional[date],
    to_date: Optional[date],
    supplier: Optional[str] = None,
) -> List[Invoice]:
    """
    Fetch invoices from the database and return them as domain Invoice entities.
    """
    con = _conn()

    from_iso = from_date.isoformat() if from_date else None
    to_iso = to_date.isoformat() if to_date else None

    if from_iso and to_iso:
        if supplier:
            header_rows = con.execute(
                "SELECT id, date, date_iso, doc_number, supplier, client, total_sum, source_path FROM invoices "
                "WHERE COALESCE(date_iso, date) IS NOT NULL "
                "AND date_iso BETWEEN ? AND ? AND supplier LIKE ? "
                "ORDER BY COALESCE(date_iso, date) ASC, id ASC",
                (from_iso, to_iso, f"%{supplier}%")
            ).fetchall()
        else:
            header_rows = con.execute(
                "SELECT id, date, date_iso, doc_number, supplier, client, total_sum, source_path FROM invoices "
                "WHERE COALESCE(date_iso, date) IS NOT NULL "
                "AND date_iso BETWEEN ? AND ? "
                "ORDER BY COALESCE(date_iso, date) ASC, id ASC",
                (from_iso, to_iso)
            ).fetchall()
    else:
        if supplier:
            header_rows = con.execute(
                "SELECT id, date, date_iso, doc_number, supplier, client, total_sum, source_path FROM invoices "
                "WHERE supplier LIKE ? "
                "ORDER BY created_at ASC, id ASC",
                (f"%{supplier}%",)
            ).fetchall()
        else:
            header_rows = con.execute(
                "SELECT id, date, date_iso, doc_number, supplier, client, total_sum, source_path FROM invoices "
                "ORDER BY created_at ASC, id ASC"
            ).fetchall()

    invoices = []
    for header_row in header_rows:
        invoice_id = header_row["id"]
        item_rows = con.execute(
            "SELECT code, name, qty, price, total FROM invoice_items WHERE invoice_id=? ORDER BY idx ASC",
            (invoice_id,)
        ).fetchall()

        header_dict = dict(header_row)
        item_dicts = [dict(item_row) for item_row in item_rows]
        invoice = _rowset_to_invoice(header_dict, item_dicts)
        invoices.append(invoice)

    con.close()
    return invoices
