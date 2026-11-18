import csv
import io
from typing import List

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from backend.domain.invoices import Invoice, InvoiceComment, InvoiceItem
from backend.handlers import texts
from backend.handlers.callback_registry import (
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
    date_str = header.invoice_date.isoformat() if header.invoice_date else texts.PLACEHOLDER
    total_str = (
        format_money(header.total_amount) if header.total_amount is not None else texts.PLACEHOLDER
    )

    return (
        f"{texts.HEADER_DOCUMENT}: {header.invoice_number or texts.PLACEHOLDER}\n"
        f"{texts.HEADER_DATE}: {date_str}\n"
        f"{texts.HEADER_SUPPLIER}: {header.supplier_name or texts.PLACEHOLDER}\n"
        f"{texts.HEADER_CLIENT}: {header.customer_name or texts.PLACEHOLDER}\n"
        f"{texts.HEADER_TOTAL}: {total_str}"
    )


def format_invoice_items(items: List[InvoiceItem]) -> str:
    if not items:
        return texts.ITEMS_NOT_RECOGNIZED

    blocks = []
    for i, item in enumerate(items, 1):
        name = (item.description or "").strip() or texts.PLACEHOLDER
        code = (item.sku or "").strip()
        qty = format_money(item.quantity)
        price = format_money(item.unit_price)
        total = format_money(item.line_total)
        title = f"{i}. {name}" if not code else f"{i}. [{code}] {name}"
        blocks.append(
            f"{title}\n   {texts.ITEM_QTY}: {qty}  |  {texts.ITEM_PRICE}: {price}  |  "
            f"{texts.ITEM_TOTAL}: {total}"
        )
    return "\n\n".join(blocks)


def format_invoice_summary(invoice: Invoice) -> str:
    header = invoice.header
    lines = []

    if header.subtotal is not None:
        lines.append(f"{texts.SUMMARY_SUBTOTAL}: {format_money(header.subtotal)}")
    if header.tax_amount is not None:
        lines.append(f"{texts.SUMMARY_TAX}: {format_money(header.tax_amount)}")
    if header.total_amount is not None:
        lines.append(f"{texts.SUMMARY_TOTAL}: {format_money(header.total_amount)}")
    if header.currency:
        lines.append(f"{texts.SUMMARY_CURRENCY}: {header.currency}")

    return "\n".join(lines) if lines else ""


def format_invoice_comments(
    comments: List[InvoiceComment],
    extra_comments: List[str] | None = None,
) -> str:
    messages: List[str] = []
    for comment in comments:
        message = (comment.message or "").strip()
        if message:
            messages.append(message)
    for raw_comment in extra_comments or []:
        if isinstance(raw_comment, str):
            message = raw_comment.strip()
            if message and message not in messages:
                messages.append(message)
    if not messages:
        return ""
    return "\n".join([texts.COMMENTS_SECTION_TITLE, *messages])


def format_invoice_full(
    invoice: Invoice,
    extra_comments: List[str] | None = None,
) -> str:
    header_text = format_invoice_header(invoice)
    items_text = format_invoice_items(invoice.items)
    summary_text = format_invoice_summary(invoice)
    comments_text = format_invoice_comments(invoice.comments, extra_comments=extra_comments)

    parts = [header_text]
    if items_text:
        parts.append(texts.SECTION_DIVIDER)
        parts.append(items_text)
    if summary_text:
        parts.append(texts.SECTION_DIVIDER)
        parts.append(summary_text)
    if comments_text:
        parts.append(texts.SECTION_DIVIDER)
        parts.append(comments_text)

    return "\n\n".join(parts)


def fmt_header(p: dict) -> str:
    return (
        f"{texts.HEADER_DOCUMENT}: {p.get('doc_number') or texts.PLACEHOLDER}\n"
        f"{texts.HEADER_DATE}: {p.get('date') or texts.PLACEHOLDER}\n"
        f"{texts.HEADER_SUPPLIER}: {p.get('supplier') or texts.PLACEHOLDER}\n"
        f"{texts.HEADER_CLIENT}: {p.get('client') or texts.PLACEHOLDER}\n"
        f"{texts.HEADER_TOTAL}: "
        f"{format_money(p['total_sum']) if p.get('total_sum') is not None else texts.PLACEHOLDER}"
    )


def fmt_items(items: list[dict]) -> str:
    if not items:
        return texts.ITEMS_NOT_RECOGNIZED

    blocks = []
    for i, it in enumerate(items, 1):
        name = (it.get("name") or "").strip() or texts.PLACEHOLDER
        code = (it.get("code") or "").strip()
        qty = format_money(it.get("qty", 0))
        price = format_money(it.get("price", 0))
        total = format_money(it.get("total", 0))
        title = f"{i}. {name}" if not code else f"{i}. [{code}] {name}"
        blocks.append(
            f"{title}\n   {texts.ITEM_QTY}: {qty}  |  {texts.ITEM_PRICE}: {price}  |  "
            f"{texts.ITEM_TOTAL}: {total}"
        )
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
                    text=texts.BUTTON_UPLOAD,
                    callback_data=CallbackAction.UPLOAD.value,
                )
            ],
            [
                InlineKeyboardButton(
                    text=texts.BUTTON_EDIT,
                    callback_data=CallbackAction.EDIT.value,
                ),
                InlineKeyboardButton(
                    text=texts.BUTTON_COMMENT,
                    callback_data=CallbackAction.COMMENT.value,
                ),
            ],
            [
                InlineKeyboardButton(
                    text=texts.BUTTON_SAVE,
                    callback_data=CallbackAction.SAVE.value,
                ),
                InlineKeyboardButton(
                    text=texts.BUTTON_PERIOD,
                    callback_data=CallbackAction.PERIOD.value,
                ),
            ],
            [
                InlineKeyboardButton(
                    text=texts.BUTTON_HELP,
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
                    text=texts.BUTTON_EDIT,
                    callback_data=CallbackAction.EDIT.value,
                ),
                InlineKeyboardButton(
                    text=texts.BUTTON_COMMENT,
                    callback_data=CallbackAction.COMMENT.value,
                ),
            ],
            [
                InlineKeyboardButton(
                    text=texts.BUTTON_SAVE,
                    callback_data=CallbackAction.SAVE.value,
                ),
                InlineKeyboardButton(
                    text=texts.BUTTON_PERIOD,
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
                    text=texts.BUTTON_SUPPLIER,
                    callback_data=CallbackHeader.SUPPLIER.value,
                ),
                InlineKeyboardButton(
                    text=texts.BUTTON_CLIENT,
                    callback_data=CallbackHeader.CLIENT.value,
                ),
            ],
            [
                InlineKeyboardButton(
                    text=texts.BUTTON_DATE,
                    callback_data=CallbackHeader.DATE.value,
                ),
                InlineKeyboardButton(
                    text=texts.BUTTON_NUMBER,
                    callback_data=CallbackHeader.DOC_NUMBER.value,
                ),
            ],
            [
                InlineKeyboardButton(
                    text=texts.BUTTON_TOTAL,
                    callback_data=CallbackHeader.TOTAL_SUM.value,
                )
            ],
            [
                InlineKeyboardButton(
                    text=texts.BUTTON_ITEMS,
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
        nav.append(
            InlineKeyboardButton(
                text=texts.BUTTON_PREV_PAGE, callback_data=make_items_page_callback(page - 1)
            )
        )
    if end < n:
        nav.append(
            InlineKeyboardButton(
                text=texts.BUTTON_NEXT_PAGE, callback_data=make_items_page_callback(page + 1)
            )
        )
    if nav:
        rows.append(nav)
    rows.append(
        [
            InlineKeyboardButton(
                text=texts.BUTTON_BACK_TO_HEADER, callback_data=CallbackAction.EDIT.value
            )
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def item_fields_kb(idx: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=texts.BUTTON_ITEM_NAME,
                    callback_data=make_item_field_callback(idx, "name"),
                )
            ],
            [
                InlineKeyboardButton(
                    text=texts.BUTTON_ITEM_QTY,
                    callback_data=make_item_field_callback(idx, "qty"),
                ),
                InlineKeyboardButton(
                    text=texts.BUTTON_ITEM_PRICE,
                    callback_data=make_item_field_callback(idx, "price"),
                ),
                InlineKeyboardButton(
                    text=texts.BUTTON_ITEM_TOTAL,
                    callback_data=make_item_field_callback(idx, "total"),
                ),
            ],
            [
                InlineKeyboardButton(
                    text=texts.BUTTON_BACK_TO_LIST,
                    callback_data=CallbackAction.ITEMS.value,
                )
            ],
        ]
    )
