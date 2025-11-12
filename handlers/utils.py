from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramBadRequest
import io
import csv

MAX_MSG = 4000  # Telegram message limit is 4096 characters


def format_money(x) -> str:
    """Format number to money string (2 decimal places, remove trailing zeros)."""
    try:
        return f"{float(x):.2f}".rstrip("0").rstrip(".")
    except:
        return str(x)


def fmt_header(p: dict) -> str:
    """Format invoice header for display."""
    return (
        f"📑 Документ: {p.get('doc_number') or '—'}\n"
        f"📅 Дата: {p.get('date') or '—'}\n"
        f"🏭 Поставщик: {p.get('supplier') or '—'}\n"
        f"👤 Клиент: {p.get('client') or '—'}\n"
        f"💰 Итого: {format_money(p['total_sum']) if p.get('total_sum') is not None else '—'}"
    )


def fmt_items(items: list[dict]) -> str:
    """Format invoice items list for display."""
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
    """Send long text in chunks (respecting Telegram message limit)."""
    for i in range(0, len(text), MAX_MSG):
        await message.answer(text[i:i+MAX_MSG])


async def safe_answer(call, text: str = "Обрабатываю…", show_alert: bool = False):
    """Safely answer callback query, ignoring errors."""
    try:
        await call.answer(text=text, show_alert=show_alert, cache_time=0)
    except TelegramBadRequest:
        pass


def csv_bytes(items: list[dict]) -> bytes:
    """Generate CSV bytes from items list."""
    sio = io.StringIO()
    w = csv.writer(sio, delimiter=';')
    w.writerow(["#", "name", "qty", "price", "total"])
    for i, it in enumerate(items, 1):
        w.writerow([
            i,
            it.get("name", ""),
            format_money(it.get("qty", 0)),
            format_money(it.get("price", 0)),
            format_money(it.get("total", 0)),
        ])
    data = sio.getvalue().encode("utf-8-sig")
    sio.close()
    return data


def main_kb() -> InlineKeyboardMarkup:
    """Main menu keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📄 Загрузить счёт", callback_data="act_upload")],
        [InlineKeyboardButton(text="✏️ Редактировать", callback_data="act_edit"),
         InlineKeyboardButton(text="💬 Комментарий", callback_data="act_comment")],
        [InlineKeyboardButton(text="💾 Сохранить", callback_data="act_save"),
         InlineKeyboardButton(text="📊 Счета за период", callback_data="act_period")],
        [InlineKeyboardButton(text="ℹ️ Помощь", callback_data="act_help")]
    ])


def actions_kb() -> InlineKeyboardMarkup:
    """Actions keyboard (after file upload)."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Редактировать", callback_data="act_edit"),
         InlineKeyboardButton(text="💬 Комментарий", callback_data="act_comment")],
        [InlineKeyboardButton(text="💾 Сохранить", callback_data="act_save"),
         InlineKeyboardButton(text="📊 Счета за период", callback_data="act_period")]
    ])


def header_kb() -> InlineKeyboardMarkup:
    """Header fields editing keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏭 Поставщик", callback_data="hed:supplier"),
         InlineKeyboardButton(text="👤 Клиент", callback_data="hed:client")],
        [InlineKeyboardButton(text="📅 Дата", callback_data="hed:date"),
         InlineKeyboardButton(text="📑 Номер", callback_data="hed:doc_number")],
        [InlineKeyboardButton(text="💰 Итого", callback_data="hed:total_sum")],
        [InlineKeyboardButton(text="📦 Позиции", callback_data="act_items")]
    ])


def items_index_kb(n: int, page: int = 1, per_page: int = 20) -> InlineKeyboardMarkup:
    """Items pagination keyboard."""
    start = (page-1)*per_page + 1
    end = min(n, page*per_page)
    rows = []
    row = []
    for i in range(start, end+1):
        row.append(InlineKeyboardButton(text=str(i), callback_data=f"item_pick:{i}"))
        if len(row) == 5:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    nav = []
    if page > 1:
        nav.append(InlineKeyboardButton(text="◀️", callback_data=f"items_page:{page-1}"))
    if end < n:
        nav.append(InlineKeyboardButton(text="▶️", callback_data=f"items_page:{page+1}"))
    if nav:
        rows.append(nav)
    rows.append([InlineKeyboardButton(text="⬅️ К шапке", callback_data="act_edit")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def item_fields_kb(idx: int) -> InlineKeyboardMarkup:
    """Item fields editing keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Название", callback_data=f"itm_field:{idx}:name")],
        [InlineKeyboardButton(text="🔢 Кол-во", callback_data=f"itm_field:{idx}:qty"),
         InlineKeyboardButton(text="💵 Цена", callback_data=f"itm_field:{idx}:price"),
         InlineKeyboardButton(text="🧮 Сумма", callback_data=f"itm_field:{idx}:total")],
        [InlineKeyboardButton(text="⬅️ К списку", callback_data="act_items")]
    ])

