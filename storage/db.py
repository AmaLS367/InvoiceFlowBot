import os, sqlite3, re
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

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

def _to_iso(d: Optional[str]) -> Optional[str]:
    if not d: return None
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
        if y < 100: y += 2000 if y <= 68 else 1900
        return f"{y:04d}-{mo:02d}-{da:02d}"
    # 2) 12 June 2025 / 12 juin 2025
    m = re.match(r"^(\d{1,2})\s+([A-Za-z\u00E9\u00EA\u00FB\u00EE\u00F4\u00E8\u00E0\u00F9\u00EF\u00EB\u00E7]+)\s+(\d{2,4})$", s, flags=re.I)
    if m:
        da = int(m.group(1))
        mon = m.group(2).lower()
        y = int(m.group(3))
        if y < 100: y += 2000 if y <= 68 else 1900
        mo = _MONTHS.get(mon)
        if mo:
            return f"{y:04d}-{mo:02d}-{da:02d}"
    return None

def save_invoice(user_id: int, parsed: Dict[str, Any], source_path: str, raw_text: Optional[str] = None, comments: Optional[List[str]] = None) -> int:
    con = _conn()
    cur = con.cursor()
    iso = _to_iso(parsed.get("date"))
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
    f_iso, t_iso = _to_iso(date_from), _to_iso(date_to)
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
    return rows

def items_count(invoice_id: int) -> int:
    con = _conn()
    n = con.execute("SELECT COUNT(1) FROM invoice_items WHERE invoice_id=?", (invoice_id,)).fetchone()[0]
    con.close()
    return int(n)
