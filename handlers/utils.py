import csv
import io
from typing import List

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from domain.invoices import Invoice, InvoiceItem
from handlers.callback_registry import (
    CallbackAction,
    CallbackHeader,
    make_item_field_callback,
    make_item_pick_callback,
    make_items_page_callback,
)

MAX_MSG = 4000  # Telegram message limit is 4096 characters


def format_money(x) -> str:
    try:
        return f"{float(x):.2f}".rstrip("0").rstrip(".")
    except (ValueError, TypeError):
        return str(x)


def format_invoice_header(invoice: Invoice) -> str:
    header = invoice.header
    date_str = header.invoice_date.isoformat() if header.invoice_date else "—"
    total_str = format_money(header.total_amount) if header.total_amount is not None else "—"

    return (
        f"📑 Документ: {header.invoice_number or '—'}\n"
        f"📅 Дата: {date_str}\n"
        f"🏭 Поставщик: {header.supplier_name or '—'}\n"
        f"👤 Клиент: {header.customer_name or '—'}\n"
        f"💰 Итого: {total_str}"
    )


def format_invoice_items(items: List[InvoiceItem]) -> str:
    if not items:
        return "Позиции не распознаны."

    blocks = []
    for i, item in enumerate(items, 1):
        name = (item.description or "").strip() or "—"
        code = (item.sku or "").strip()
        qty = format_money(item.quantity)
        price = format_money(item.unit_price)
        total = format_money(item.line_total)
        title = f"{i}. {name}" if not code else f"{i}. [{code}] {name}"
        blocks.append(f"{title}\n   Кол-во: {qty}  |  Цена: {price}  |  Сумма: {total}")
    return "\n\n".join(blocks)


def format_invoice_summary(invoice: Invoice) -> str:
    header = invoice.header
    lines = []

    if header.subtotal is not None:
        lines.append(f"Подытог: {format_money(header.subtotal)}")
    if header.tax_amount is not None:
        lines.append(f"НДС: {format_money(header.tax_amount)}")
    if header.total_amount is not None:
        lines.append(f"Итого: {format_money(header.total_amount)}")
    if header.currency:
        lines.append(f"Валюта: {header.currency}")

    return "\n".join(lines) if lines else ""


def format_invoice_full(invoice: Invoice) -> str:
    header_text = format_invoice_header(invoice)
    items_text = format_invoice_items(invoice.items)
    summary_text = format_invoice_summary(invoice)

    parts = [header_text]
    if items_text:
        parts.append("—" * 34)
        parts.append(items_text)
    if summary_text:
        parts.append("—" * 34)
        parts.append(summary_text)

    return "\n\n".join(parts)


def fmt_header(p: dict) -> str:
    return (
        f"📑 Документ: {p.get('doc_number') or '—'}\n"
        f"📅 Дата: {p.get('date') or '—'}\n"
        f"🏭 Поставщик: {p.get('supplier') or '—'}\n"
        f"👤 Клиент: {p.get('client') or '—'}\n"
        f"💰 Итого: {format_money(p['total_sum']) if p.get('total_sum') is not None else '—'}"
    )


def fmt_items(items: list[dict]) -> str:
    if not items:
        return "Позиции не распознаны."

    blocks = []
    for i, it in enumerate(items, 1):
        name = (it.get("name") or "").strip() or "—"
        code = (it.get("code") or "").strip()
        qty = format_money(it.get("qty", 0))
        price = format_money(it.get("price", 0))
        total = format_money(it.get("total", 0))
        title = f"{i}. {name}" if not code else f"{i}. [{code}] {name}"
        blocks.append(f"{title}\n   Кол-во: {qty}  |  Цена: {price}  |  Сумма: {total}")
    return "\n\n".join(blocks)


async def send_chunked(message: Message, text: str):
    for i in range(0, len(text), MAX_MSG):
        await message.answer(text[i : i + MAX_MSG])


def csv_bytes_from_items(items: List[InvoiceItem]) -> bytes:
    sio = io.StringIO()
    w = csv.writer(sio, delimiter=";")
    w.writerow(["#", "name", "qty", "price", "total"])
    for i, item in enumerate(items, 1):
        w.writerow(
            [
                i,
                item.description or "",
                format_money(item.quantity),
                format_money(item.unit_price),
                format_money(item.line_total),
            ]
        )
    data = sio.getvalue().encode("utf-8-sig")
    sio.close()
    return data


def csv_bytes(items: list[dict]) -> bytes:
    """
    Backwards compatible adapter: generate CSV bytes from list of dicts.
    """
    sio = io.StringIO()
    w = csv.writer(sio, delimiter=";")
    w.writerow(["#", "name", "qty", "price", "total"])
    for i, it in enumerate(items, 1):
        w.writerow(
            [
                i,
                it.get("name", ""),
                format_money(it.get("qty", 0)),
                format_money(it.get("price", 0)),
                format_money(it.get("total", 0)),
            ]
        )
    data = sio.getvalue().encode("utf-8-sig")
    sio.close()
    return data


def main_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📄 Загрузить счёт",
                    callback_data=CallbackAction.UPLOAD.value,
                )
            ],
            [
                InlineKeyboardButton(
                    text="✏️ Редактировать",
                    callback_data=CallbackAction.EDIT.value,
                ),
                InlineKeyboardButton(
                    text="💬 Комментарий",
                    callback_data=CallbackAction.COMMENT.value,
                ),
            ],
            [
                InlineKeyboardButton(
                    text="💾 Сохранить",
                    callback_data=CallbackAction.SAVE.value,
                ),
                InlineKeyboardButton(
                    text="📊 Счета за период",
                    callback_data=CallbackAction.PERIOD.value,
                ),
            ],
            [
                InlineKeyboardButton(
                    text="ℹ️ Помощь",
                    callback_data=CallbackAction.HELP.value,
                )
            ],
        ]
    )


def actions_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✏️ Редактировать",
                    callback_data=CallbackAction.EDIT.value,
                ),
                InlineKeyboardButton(
                    text="💬 Комментарий",
                    callback_data=CallbackAction.COMMENT.value,
                ),
            ],
            [
                InlineKeyboardButton(
                    text="💾 Сохранить",
                    callback_data=CallbackAction.SAVE.value,
                ),
                InlineKeyboardButton(
                    text="📊 Счета за период",
                    callback_data=CallbackAction.PERIOD.value,
                ),
            ],
        ]
    )


def header_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🏭 Поставщик",
                    callback_data=CallbackHeader.SUPPLIER.value,
                ),
                InlineKeyboardButton(
                    text="👤 Клиент",
                    callback_data=CallbackHeader.CLIENT.value,
                ),
            ],
            [
                InlineKeyboardButton(
                    text="📅 Дата",
                    callback_data=CallbackHeader.DATE.value,
                ),
                InlineKeyboardButton(
                    text="📑 Номер",
                    callback_data=CallbackHeader.DOC_NUMBER.value,
                ),
            ],
            [
                InlineKeyboardButton(
                    text="💰 Итого",
                    callback_data=CallbackHeader.TOTAL_SUM.value,
                )
            ],
            [
                InlineKeyboardButton(
                    text="📦 Позиции",
                    callback_data=CallbackAction.ITEMS.value,
                )
            ],
        ]
    )


def items_index_kb(n: int, page: int = 1, per_page: int = 20) -> InlineKeyboardMarkup:
    start = (page - 1) * per_page + 1
    end = min(n, page * per_page)
    rows = []
    row = []
    for i in range(start, end + 1):
        row.append(InlineKeyboardButton(text=str(i), callback_data=make_item_pick_callback(i)))
        if len(row) == 5:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    nav = []
    if page > 1:
        nav.append(InlineKeyboardButton(text="◀️", callback_data=make_items_page_callback(page - 1)))
    if end < n:
        nav.append(InlineKeyboardButton(text="▶️", callback_data=make_items_page_callback(page + 1)))
    if nav:
        rows.append(nav)
    rows.append([InlineKeyboardButton(text="⬅️ К шапке", callback_data=CallbackAction.EDIT.value)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def item_fields_kb(idx: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✏️ Название",
                    callback_data=make_item_field_callback(idx, "name"),
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔢 Кол-во",
                    callback_data=make_item_field_callback(idx, "qty"),
                ),
                InlineKeyboardButton(
                    text="💵 Цена",
                    callback_data=make_item_field_callback(idx, "price"),
                ),
                InlineKeyboardButton(
                    text="🧮 Сумма",
                    callback_data=make_item_field_callback(idx, "total"),
                ),
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ К списку",
                    callback_data=CallbackAction.ITEMS.value,
                )
            ],
        ]
    )
