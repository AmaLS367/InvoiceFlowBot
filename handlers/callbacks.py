"""
Callback handlers for invoice editing and actions.
"""
import time
import uuid

from aiogram import F, Router
from aiogram.types import CallbackQuery, ForceReply, Message

from domain.invoices import InvoiceComment
from handlers.state import PENDING_EDIT, PENDING_PERIOD
from handlers.utils import (
    format_invoice_header,
    format_money,
    header_kb,
    item_fields_kb,
    items_index_kb,
)
from ocr.engine.util import get_logger, set_request_id
from services.draft_service import (
    clear_current_draft,
    get_current_draft,
)
from services.invoice_service import save_invoice as save_invoice_service

router = Router()
logger = get_logger("ocr.engine")


@router.callback_query(F.data == "act_edit")
async def cb_act_edit(call: CallbackQuery):
    """Handle edit action callback - show header editing options."""
    req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    set_request_id(req)
    logger.info(f"[TG] update start req={req} h=cb_act_edit")
    uid = call.from_user.id
    draft = await get_current_draft(uid)
    if draft is None:
        if call.message is not None:
            await call.message.answer("Нет черновика. Пришлите документ.")
            await call.answer()
        return
    
    invoice = draft.invoice
    head_text = format_invoice_header(invoice)
    
    if call.message is not None:
        await call.message.answer(head_text + "\nВыберите поле для редактирования:", reply_markup=header_kb())
        await call.answer()
    logger.info(f"[TG] update done req={req} h=cb_act_edit")


@router.callback_query(F.data.startswith("hed:"))
async def cb_hed_field(call: CallbackQuery):
    """Handle header field selection for editing."""
    req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    set_request_id(req)
    logger.info(f"[TG] update start req={req} h=cb_hed_field")
    uid = call.from_user.id
    draft = await get_current_draft(uid)
    if draft is None:
        await call.answer()
        return
    
    if call.data is not None:
        field = call.data.split(":",1)[1]
        nice = {"supplier":"Поставщик","client":"Клиент","date":"Дата","doc_number":"Номер","total_sum":"Итого"}[field]
    PENDING_EDIT[uid] = {"kind":"header","key":field}
    if call.message is not None:
        await call.message.answer(f"Введите новое значение для «{nice}»:", reply_markup=ForceReply(selective=True))
        await call.answer()
    logger.info(f"[TG] update done req={req} h=cb_hed_field")


@router.callback_query(F.data == "act_items")
async def cb_act_items(call: CallbackQuery):
    """Handle items action callback - show items list for editing."""
    req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    set_request_id(req)
    logger.info(f"[TG] update start req={req} h=cb_act_items")
    uid = call.from_user.id
    draft = await get_current_draft(uid)
    if draft is None:
        await call.answer()
        return
    
    invoice = draft.invoice
    n = len(invoice.items)
    
    if n == 0:
        if call.message is not None:
            await call.message.answer("Позиции не распознаны.")
            await call.answer()
        return
    
    if call.message is not None:
        await call.message.answer(f"Выберите позицию для редактирования (всего: {n}):", reply_markup=items_index_kb(n, 1))
        await call.answer()
    logger.info(f"[TG] update done req={req} h=cb_act_items")


@router.callback_query(F.data.startswith("items_page:"))
async def cb_items_page(call: CallbackQuery):
    """Handle items pagination callback."""
    req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    set_request_id(req)
    logger.info(f"[TG] update start req={req} h=cb_items_page")
    uid = call.from_user.id
    draft = await get_current_draft(uid)
    if draft is None:
        await call.answer()
        return
        
    if call.data is not None:
        page = int(call.data.split(":")[1])
        invoice = draft.invoice
        n = len(invoice.items)
        
        if call.message is not None:
            if isinstance(call.message, Message):
                await call.message.edit_reply_markup(reply_markup=items_index_kb(n, page))
                await call.answer()
    logger.info(f"[TG] update done req={req} h=cb_items_page")


@router.callback_query(F.data.startswith("item_pick:"))
async def cb_item_pick(call: CallbackQuery):
    """Handle item selection callback - show item details for editing."""
    req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    set_request_id(req)
    logger.info(f"[TG] update start req={req} h=cb_item_pick")
    uid = call.from_user.id
    draft = await get_current_draft(uid)
    if draft is None:
        await call.answer()
        return
    
    if call.data is not None:
        idx = int(call.data.split(":")[1])
    
    invoice = draft.invoice
    items = invoice.items
    if not (1 <= idx <= len(items)):
        await call.answer()
        return
    item = items[idx-1]
    text = (
        f"#{idx}\n"
        f"Название: {item.description or ''}\n"
        f"Код: {item.sku or ''}\n"
        f"Кол-во: {format_money(item.quantity)} | Цена: {format_money(item.unit_price)} | Сумма: {format_money(item.line_total)}"
    )
    
    if call.message is not None:
        await call.message.answer(text, reply_markup=item_fields_kb(idx))
        await call.answer()
    logger.info(f"[TG] update done req={req} h=cb_item_pick")


@router.callback_query(F.data.startswith("itm_field:"))
async def cb_itm_field(call: CallbackQuery):
    """Handle item field selection for editing."""
    req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    set_request_id(req)
    logger.info(f"[TG] update start req={req} h=cb_itm_field")
    uid = call.from_user.id
    if call.data is None:
        await call.answer()
        return
    parts = call.data.split(":")
    idx = int(parts[1])
    key = parts[2]  # name/qty/price/total
    nice = {"name":"Название","qty":"Кол-во","price":"Цена","total":"Сумма"}[key]
    PENDING_EDIT[uid] = {"kind":"item","idx":idx,"key":key}
    if call.message is not None:
        await call.message.answer(f"Введите новое значение для «{nice}» у позиции #{idx}:", reply_markup=ForceReply(selective=True))
        await call.answer()
    logger.info(f"[TG] update done req={req} h=cb_itm_field")


@router.callback_query(F.data == "act_comment")
async def cb_act_comment(call: CallbackQuery):
    """Handle comment action callback - prompt for comment input."""
    req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    set_request_id(req)
    logger.info(f"[TG] update start req={req} h=cb_act_comment")

    uid = call.from_user.id
    draft = await get_current_draft(uid)
    if draft is None:
        if call.message is not None:
            await call.message.answer("Нет черновика. Пришлите документ.")
        await call.answer()
        return

    PENDING_EDIT[uid] = {"kind": "comment"}
    if call.message is not None:
        await call.message.answer("Комментарий к счёту:", reply_markup=ForceReply(selective=True))
    await call.answer()
    logger.info(f"[TG] update done req={req} h=cb_act_comment")


@router.callback_query(F.data == "act_save")
async def cb_act_save(call: CallbackQuery):
    """Handle save action callback - save invoice to database."""
    req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    set_request_id(req)
    logger.info(f"[TG] update start req={req} h=cb_act_save")

    uid = call.from_user.id
    draft = await get_current_draft(uid)
    if draft is None:
        if call.message is not None:
            await call.message.answer("Нет черновика. Пришлите документ.")
        await call.answer()
        return

    invoice = draft.invoice
    comments = list(draft.comments)

    # Auto-comment for sum mismatch
    header_sum = float(invoice.header.total_amount) if invoice.header.total_amount is not None else 0.0
    sum_items = sum(float(item.line_total) for item in invoice.items)
    diff = round(sum_items - header_sum, 2)
    
    if abs(diff) >= 0.01:
        doc_number = invoice.header.invoice_number or "—"
        supplier = invoice.header.supplier_name or "—"
        auto_text = (
            f"[auto] Несходство суммы: по позициям {sum_items:.2f}, "
            f"в шапке {header_sum:.2f}, разница {diff:+.2f}. "
            f"Документ: {doc_number}, Поставщик: {supplier}."
        )
        if auto_text not in comments:
            invoice.comments.append(InvoiceComment(message=auto_text))

    inv_id = await save_invoice_service(invoice, uid)
    await clear_current_draft(uid)
    if call.message is not None:
        await call.message.answer(f"Сохранено в БД. ID счета: {inv_id}")
    await call.answer()
    logger.info(f"[TG] update done req={req} h=cb_act_save")


@router.callback_query(F.data == "act_period")
async def cb_act_period(call: CallbackQuery):
    """Handle period action callback - prompt for date range input."""
    req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    set_request_id(req)
    logger.info(f"[TG] update start req={req} h=cb_act_period")
    uid = call.from_user.id
    PENDING_PERIOD[uid] = {"step": "from"}
    if call.message is not None:
        await call.message.answer("С даты (YYYY-MM-DD):", reply_markup=ForceReply(selective=True))
        await call.answer()
    logger.info(f"[TG] update done req={req} h=cb_act_period")


@router.callback_query(F.data == "act_upload")
async def cb_act_upload(call: CallbackQuery):
    """Handle upload action callback - prompt for file upload."""
    req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    set_request_id(req)
    logger.info(f"[TG] update start req={req} h=cb_act_upload")

    if call.message is not None:
        await call.message.answer("Пришлите файл: PDF или фото накладной. Бот распознаёт и покажет черновик.")
        await call.answer()
    
    logger.info(f"[TG] update done req={req} h=cb_act_upload")


@router.callback_query(F.data == "act_help")
async def cb_act_help(call: CallbackQuery):
    """Handle help action callback - show help message."""
    req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    set_request_id(req)
    logger.info(f"[TG] update start req={req} h=cb_act_help")

    if call.message is not None:
        await call.message.answer(
            "Подсказка:\n"
            "1) Пришлите PDF/фото счёта\n"
            "2) /show для просмотра\n"
            "3) /edit и /edititem для правок, /comment для заметок\n"
            "4) /save чтобы сохранить в БД\n"
            "5) /invoices <с> <по> [supplier=...] для выборки"
        )
        await call.answer()

    logger.info(f"[TG] update done req={req} h=cb_act_help")

