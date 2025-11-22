from __future__ import annotations

import json
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, Optional

import aiosqlite

from domain.drafts import InvoiceDraft
from domain.invoices import (
    Invoice,
    InvoiceComment,
    InvoiceHeader,
    InvoiceItem,
    InvoiceSourceInfo,
)
from storage.db import DB_PATH


async def _connect() -> aiosqlite.Connection:
    """
    Open an aiosqlite connection for the drafts database and configure row factory.
    """
    connection = await aiosqlite.connect(DB_PATH)
    connection.row_factory = aiosqlite.Row
    return connection


def _draft_to_payload(draft: InvoiceDraft) -> str:
    """
    Serialize an InvoiceDraft into a JSON string that can be stored in the database.

    The payload must only contain JSON-serializable primitives.
    """

    def convert_value(value: Any) -> Any:
        if isinstance(value, datetime):
            return {"__type__": "datetime", "value": value.isoformat()}
        if isinstance(value, date):
            return {"__type__": "date", "value": value.isoformat()}
        if isinstance(value, Decimal):
            return {"__type__": "decimal", "value": str(value)}
        if isinstance(value, list):
            return [convert_value(item) for item in value]
        if isinstance(value, dict):
            return {str(k): convert_value(v) for k, v in value.items()}
        # Handle dataclass objects
        if hasattr(value, "__dict__"):
            return convert_value(value.__dict__)
        return value

    invoice_dict = draft.invoice.__dict__
    payload: Dict[str, Any] = {
        "invoice": convert_value(invoice_dict),
        "path": draft.path,
        "raw_text": draft.raw_text,
        "comments": list(draft.comments),
    }
    return json.dumps(payload, ensure_ascii=False)


def _payload_to_draft(payload_str: str) -> Optional[InvoiceDraft]:
    """
    Deserialize a JSON payload from the database back into an InvoiceDraft.

    If the payload is invalid, returns None.
    """
    try:
        raw = json.loads(payload_str)
    except json.JSONDecodeError:
        return None

    if not isinstance(raw, dict):
        return None

    def restore_value(value: Any) -> Any:
        if isinstance(value, dict) and "__type__" in value and "value" in value:
            type_marker = value["__type__"]
            data = value["value"]
            if type_marker == "datetime":
                return datetime.fromisoformat(data)
            if type_marker == "date":
                return date.fromisoformat(data)
            if type_marker == "decimal":
                return Decimal(data)
        if isinstance(value, list):
            return [restore_value(item) for item in value]
        if isinstance(value, dict):
            return {k: restore_value(v) for k, v in value.items()}
        return value

    invoice_payload = raw.get("invoice")
    if not isinstance(invoice_payload, dict):
        return None

    restored_invoice_dict = restore_value(invoice_payload)
    if not isinstance(restored_invoice_dict, dict):
        return None

    # Reconstruct nested dataclass objects
    header_dict = restored_invoice_dict.get("header")
    if isinstance(header_dict, dict):
        restored_invoice_dict["header"] = InvoiceHeader(**header_dict)

    items_list = restored_invoice_dict.get("items")
    if isinstance(items_list, list):
        restored_invoice_dict["items"] = [
            InvoiceItem(**item) if isinstance(item, dict) else item
            for item in items_list
        ]

    comments_list = restored_invoice_dict.get("comments")
    if isinstance(comments_list, list):
        restored_invoice_dict["comments"] = [
            InvoiceComment(**comment) if isinstance(comment, dict) else comment
            for comment in comments_list
        ]

    source_dict = restored_invoice_dict.get("source")
    if isinstance(source_dict, dict):
        restored_invoice_dict["source"] = InvoiceSourceInfo(**source_dict)
    elif source_dict is None:
        restored_invoice_dict["source"] = None

    invoice = Invoice(**restored_invoice_dict)

    path = str(raw.get("path") or "")
    raw_text = str(raw.get("raw_text") or "")
    comments_raw = raw.get("comments") or []

    if not isinstance(comments_raw, list):
        comments = [str(comments_raw)]
    else:
        comments = [str(c) for c in comments_raw]

    return InvoiceDraft(
        invoice=invoice,
        path=path,
        raw_text=raw_text,
        comments=comments,
    )


async def save_draft_invoice(user_id: int, draft: InvoiceDraft) -> None:
    """
    Save or replace a draft invoice for the given user ID.
    """
    payload = _draft_to_payload(draft)
    connection = await _connect()
    try:
        await connection.execute(
            """
            INSERT INTO invoice_drafts(user_id, payload, created_at)
            VALUES(?, ?, datetime('now'))
            ON CONFLICT(user_id) DO UPDATE SET
                payload=excluded.payload,
                created_at=excluded.created_at
            """,
            (user_id, payload),
        )
        await connection.commit()
    finally:
        await connection.close()


async def load_draft_invoice(user_id: int) -> Optional[InvoiceDraft]:
    """
    Load a draft invoice for the given user ID, or None if it does not exist or is invalid.
    """
    connection = await _connect()
    try:
        cursor = await connection.execute(
            "SELECT payload FROM invoice_drafts WHERE user_id=?",
            (user_id,),
        )
        row = await cursor.fetchone()
        if row is None:
            return None
        payload_str = row["payload"]
        if not isinstance(payload_str, str):
            return None
        return _payload_to_draft(payload_str)
    finally:
        await connection.close()


async def delete_draft_invoice(user_id: int) -> None:
    """
    Delete a draft invoice for the given user ID if it exists.
    """
    connection = await _connect()
    try:
        await connection.execute(
            "DELETE FROM invoice_drafts WHERE user_id=?",
            (user_id,),
        )
        await connection.commit()
    finally:
        await connection.close()


__all__ = [
    "save_draft_invoice",
    "load_draft_invoice",
    "delete_draft_invoice",
]

