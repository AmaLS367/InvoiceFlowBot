"""
Synchronous database utilities and Alembic-based schema initialization.

This module exposes DB_PATH and init_db used by the rest of the application.
"""

from __future__ import annotations

import re
import sqlite3
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

import config
from alembic import command
from alembic.config import Config
from domain.invoices import Invoice
from storage.mappers import (
    db_row_to_invoice,
    invoice_item_to_db_row,
    invoice_to_db_row,
)

DB_PATH: str = config.DB_PATH


def _get_alembic_config() -> Config:
    """
    Build an Alembic Config instance pointing to the alembic.ini file
    located in the project root directory.
    """
    base_dir = Path(__file__).resolve().parent.parent
    alembic_ini = base_dir / "alembic.ini"
    config = Config(str(alembic_ini))
    return config


def _conn():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def init_db() -> None:
    """
    Apply all Alembic migrations and ensure the SQLite schema is up to date.
    """
    config = _get_alembic_config()
    # Set database URL in config so alembic/env.py can use it
    database_url = f"sqlite:///{DB_PATH}"
    config.set_main_option("sqlalchemy.url", database_url)
    command.upgrade(config, "head")


_MONTHS = {
    # Russian
    "января": 1,
    "февраля": 2,
    "марта": 3,
    "апреля": 4,
    "мая": 5,
    "июня": 6,
    "июля": 7,
    "августа": 8,
    "сентября": 9,
    "октября": 10,
    "ноября": 11,
    "декабря": 12,
    # English
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
    # French
    "janvier": 1,
    "février": 2,
    "fevrier": 2,
    "mars": 3,
    "avril": 4,
    "mai": 5,
    "juin": 6,
    "juillet": 7,
    "août": 8,
    "aout": 8,
    "septembre": 9,
    "octobre": 10,
    "novembre": 11,
    "décembre": 12,
    "decembre": 12,
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
    m = re.match(
        r"^(\d{1,2})\s+([A-Za-z\u00E9\u00EA\u00FB\u00EE\u00F4\u00E8\u00E0\u00F9\u00EF\u00EB\u00E7]+)\s+(\d{2,4})$",
        s,
        flags=re.I,
    )
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


def save_invoice(
    user_id: int,
    parsed: Dict[str, Any],
    source_path: str,
    raw_text: Optional[str] = None,
    comments: Optional[List[str]] = None,
) -> int:
    con = _conn()
    cur = con.cursor()
    iso = to_iso(parsed.get("date"))
    cur.execute(
        """
        INSERT INTO invoices(user_id, supplier, client, doc_number, date, date_iso, total_sum, raw_text, source_path)
        VALUES(?,?,?,?,?,?,?,?,?)
    """,
        (
            user_id,
            parsed.get("supplier"),
            parsed.get("client"),
            parsed.get("doc_number"),
            parsed.get("date"),
            iso,
            parsed.get("total_sum"),
            raw_text or "",
            source_path,
        ),
    )
    invoice_id = cur.lastrowid
    for i, it in enumerate(parsed.get("items") or [], 1):
        cur.execute(
            """
            INSERT INTO invoice_items(invoice_id, idx, code, name, qty, price, total)
            VALUES(?,?,?,?,?,?,?)
        """,
            (
                invoice_id,
                i,
                it.get("code") or "",
                it.get("name") or "",
                float(it.get("qty") or 0),
                float(it.get("price") or 0),
                float(it.get("total") or 0),
            ),
        )
    for text in comments or []:
        cur.execute(
            "INSERT INTO comments(invoice_id, user_id, text) VALUES(?,?,?)",
            (invoice_id, user_id, text),
        )
    con.commit()
    con.close()
    return int(invoice_id or 0)


def items_count(invoice_id: int) -> int:
    con = _conn()
    n = con.execute(
        "SELECT COUNT(1) FROM invoice_items WHERE invoice_id=?", (invoice_id,)
    ).fetchone()[0]
    con.close()
    return int(n)


# Mapping functions moved to storage/mappers.py
# Keep old function names as aliases for backward compatibility
_invoice_to_db_header = invoice_to_db_row
_invoice_item_to_db_row = invoice_item_to_db_row
_rowset_to_invoice = db_row_to_invoice


def _run_async(coro) -> Any:
    """
    Helper to run async coroutine from sync context.
    Handles both cases: when event loop is running and when it's not.
    """
    import asyncio
    import threading
    from typing import cast

    try:
        asyncio.get_running_loop()
    except RuntimeError:
        # No event loop running, create a new one
        return cast(Any, asyncio.run(coro))
    else:
        # Event loop is running, run in a new thread with a new event loop
        # This is needed when sync functions are called from async context (e.g., in tests)
        result: Any = None
        exception: Exception | None = None

        def run_in_thread() -> None:
            nonlocal result, exception
            try:
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                result = new_loop.run_until_complete(coro)
                new_loop.close()
            except Exception as e:
                exception = e

        thread = threading.Thread(target=run_in_thread)
        thread.start()
        thread.join()

        if exception:
            raise exception
        return cast(Any, result)


def save_invoice_domain(invoice: Invoice, user_id: int = 0) -> int:
    """
    Persist a domain Invoice into the database and return the created invoice ID.

    This is a thin wrapper over AsyncInvoiceStorage.save_invoice for backward compatibility.
    All SQL logic is in the async layer.
    """
    from typing import cast

    from storage.db_async import AsyncInvoiceStorage

    storage = AsyncInvoiceStorage(database_path=DB_PATH)
    return cast(int, _run_async(storage.save_invoice(invoice, user_id=user_id)))


def fetch_invoices_domain(
    from_date: Optional[date],
    to_date: Optional[date],
    supplier: Optional[str] = None,
) -> List[Invoice]:
    """
    Fetch invoices from the database and return them as domain Invoice entities.

    This is a thin wrapper over AsyncInvoiceStorage.fetch_invoices for backward compatibility.
    All SQL logic is in the async layer.
    """
    from typing import cast

    from storage.db_async import AsyncInvoiceStorage

    storage = AsyncInvoiceStorage(database_path=DB_PATH)
    return cast(
        List[Invoice],
        _run_async(storage.fetch_invoices(from_date=from_date, to_date=to_date, supplier=supplier)),
    )
