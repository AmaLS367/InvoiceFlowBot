from aiogram import Router, F
from aiogram.types import Message, BufferedInputFile, CallbackQuery

from handlers.commands import cb_act_edit as cb_act_edit_impl
from handlers.commands import cb_act_period as cb_act_period_impl
from handlers.state import PENDING_EDIT, CURRENT_PARSE
from handlers.utils import (
    fmt_header, fmt_items, send_chunked, csv_bytes,
    main_kb, actions_kb, MAX_MSG
)

from aiogram.types import ForceReply
from services.invoice_service import process_invoice_file, save_invoice
from domain.invoices import Invoice
from ocr.engine.util import get_logger, set_request_id, save_file
from storage.db import init_db
from pathlib import Path
from PIL import Image, ImageOps

import time
import uuid
import os

router = Router()
init_db()
logger = get_logger("ocr.engine")


def _invoice_to_dict(invoice: Invoice) -> dict:
    """
    Temporary adapter to keep existing utils working with plain dicts.
    Will be removed once utils are migrated to work with Invoice directly.
    """
    header = invoice.header
    items = []
    for item in invoice.items:
        items.append({
            "name": item.description or "",
            "code": item.sku or "",
            "qty": float(item.quantity),
            "price": float(item.unit_price),
            "total": float(item.line_total),
        })
    
    return {
        "supplier": header.supplier_name,
        "client": header.customer_name,
        "date": header.invoice_date.isoformat() if header.invoice_date else None,
        "doc_number": header.invoice_number,
        "total_sum": float(header.total_amount) if header.total_amount is not None else None,
        "items": items,
    }


@router.message(F.text == "/start")
async def cmd_start(message: Message):
    req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    set_request_id(req)
    logger.info(f"[TG] update start req={req} h=cmd_start")

    await message.answer(
        "Готов принять PDF/фото накладной и превратить в данные.\n"
        "Порядок: 1) пришлите файл, 2) проверьте/отредактируйте, "
        "3) сохраните в БД, 4) при необходимости запросите счета за период.",
        reply_markup=main_kb()
    )

    logger.info(f"[TG] update done req={req} h=cmd_start")

@router.message(F.text == "/help")
async def cmd_help(message: Message):
    req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    set_request_id(req)
    logger.info(f"[TG] update start req={req} h=cmd_help")

    await message.answer(
        "Команды:\n"
        "• /show — показать текущий черновик\n"
        "• /edit supplier=... client=... date=YYYY-MM-DD doc=... total=123.45\n"
        "• /edititem <index> name=... qty=... price=... total=...\n"
        "• /comment ваш_текст — добавить комментарий\n"
        "• /save — сохранить черновик в БД\n"
        "• /invoices YYYY-MM-DD YYYY-MM-DD [supplier=ТЕКСТ] — выборка счетов",
        reply_markup=main_kb()
    )
    logger.info(f"[TG] update done req={req} h=cmd_help")

@router.message(F.gif | F.animation)
async def cmd_gif(message: Message):
    req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    set_request_id(req)
    logger.info(f"[TG] update start req={req} h=cmd_gif")

    await message.answer("Я не умею обрабатывать GIF-анимации. Пришлите PDF или фото накладной.")

    logger.info(f"[TG] update done req={req} h=cmd_gif")

@router.message(F.document | F.photo)
async def handle_doc_or_photo(message: Message):
    req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    set_request_id(req)
    logger.info(f"[TG] update start req={req} h=handle_doc_or_photo")

    file = None
    if message.document:
        file = message.document
    elif message.photo:
        file = message.photo[-1]

    if not file:
        await message.answer("Не удалось получить файл.")
        return
    
    if message.bot is None:
        await message.answer("Ошибка: бот недоступен")
        return
    
    path = await save_file(file, message.bot) 
    if path is None:
        await message.answer("Ошибка при сохранении файла")
        return
    
    # Convert HEIC/HEIF/WebP to JPEG
    ext = os.path.splitext(path)[1].lower()
    if ext in {".heic", ".heif", ".webp"}:
        im = Image.open(path).convert("RGB")
        new_path = path.rsplit(".", 1)[0] + ".jpg"
        im.save(new_path, format="JPEG", quality=95)
        path = new_path
        
    # Normalize photo: EXIF rotation and convert to JPEG
    if not path.lower().endswith(".pdf"):
        try:
            img = Image.open(path)
            img = ImageOps.exif_transpose(img).convert("RGB")
            ext = Path(path).suffix.lower()
            new_path = path if ext in {".jpg", ".jpeg", ".png"} else str(Path(path).with_suffix(".jpg"))
            img.save(new_path, format="JPEG", quality=95, optimize=True)
            path = new_path
        except Exception:
            pass
    uid = message.from_user.id if message.from_user else 0
    await message.answer("📥 Получил файл. Распознаю…")

    try:
        invoice = process_invoice_file(pdf_path=path, fast=True, max_pages=12)
    except Exception as e:
        logger.exception(f"[TG] OCR failed: {e}")
        await message.answer("Ошибка при распознавании файла. Попробуйте другой файл.")
        return

    # Convert to dict for compatibility with existing utils and state
    parsed = _invoice_to_dict(invoice)
    
    # Save draft in memory (store both Invoice and dict for compatibility)
    CURRENT_PARSE[uid] = {
        "invoice": invoice,
        "parsed": parsed,
        "path": path,
        "raw_text": "",  # Not available from service layer
        "comments": []
    }

    head_text = fmt_header(parsed)
    items = parsed.get("items") or []
    items_text = fmt_items(items) if items else "Позиции не распознаны."
    full = f"{head_text}\n\n" + "—"*34 + f"\n\n{items_text}"

    if len(full) <= MAX_MSG:
        await message.answer(full, reply_markup=actions_kb())
    else:
        await message.answer(head_text, reply_markup=actions_kb())
        if len(items) > 60 or len(items_text) > MAX_MSG * 2:
            await message.answer("Таблица длинная, отправляю CSV.")
            await message.answer_document(BufferedInputFile(csv_bytes(items), filename="invoice_items.csv"))
        await send_chunked(message, items_text)
    logger.info(f"[TG] update done req={req} h=handle_doc_or_photo")


# Action buttons
@router.callback_query(F.data == "act_edit")

async def cb_act_edit(call: CallbackQuery):
    req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    set_request_id(req)
    logger.info(f"[TG] update start req={req} h=cb_act_edit")

    await cb_act_edit_impl(call)

    logger.info(f"[TG] update done req={req} h=cb_act_edit")

@router.callback_query(F.data == "act_comment")
async def cb_act_comment(call: CallbackQuery):
    req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    set_request_id(req)
    logger.info(f"[TG] update start req={req} h=cb_act_comment")

    uid = call.from_user.id
    if uid not in CURRENT_PARSE:
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
    req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    set_request_id(req)
    logger.info(f"[TG] update start req={req} h=cb_act_save")

    uid = call.from_user.id
    if uid not in CURRENT_PARSE:
        if call.message is not None:
            await call.message.answer("Нет черновика. Пришлите документ.")
        await call.answer()
        return

    # Get draft and prepare data for saving
    draft = CURRENT_PARSE.pop(uid)
    invoice = draft.get("invoice")
    
    # If invoice is not in state, reconstruct from parsed dict
    if invoice is None:
        parsed = draft["parsed"]
        # Reconstruct Invoice from dict (fallback for compatibility)
        from domain.invoices import InvoiceHeader, InvoiceItem
        from decimal import Decimal
        
        header = InvoiceHeader(
            supplier_name=parsed.get("supplier"),
            customer_name=parsed.get("client"),
            invoice_number=parsed.get("doc_number"),
            invoice_date=None,  # Would need parsing
            total_amount=Decimal(str(parsed.get("total_sum", 0))) if parsed.get("total_sum") else None,
        )
        items = []
        for it in parsed.get("items", []):
            items.append(InvoiceItem(
                description=it.get("name", ""),
                sku=it.get("code"),
                quantity=Decimal(str(it.get("qty", 0))),
                unit_price=Decimal(str(it.get("price", 0))),
                line_total=Decimal(str(it.get("total", 0))),
            ))
        invoice = Invoice(header=header, items=items)
    
    comments = list(draft.get("comments", []))

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
            from domain.invoices import InvoiceComment
            invoice.comments.append(InvoiceComment(message=auto_text))

    inv_id = save_invoice(invoice, user_id=uid)
    if call.message is not None:
        await call.message.answer(f"Сохранено в БД. ID счета: {inv_id}")
    await call.answer()
    logger.info(f"[TG] update done req={req} h=cb_act_save")


@router.callback_query(F.data == "act_period")
async def cb_act_period_bridge(call: CallbackQuery):
    req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    set_request_id(req)
    logger.info(f"[TG] update start req={req} h=cb_act_period_bridge")

    await cb_act_period_impl(call)

    logger.info(f"[TG] update done req={req} h=cb_act_period_bridge")

@router.callback_query(F.data == "act_upload")
async def cb_act_upload(call: CallbackQuery):
    req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    set_request_id(req)
    logger.info(f"[TG] update start req={req} h=cb_act_upload")

    if call.message is not None:
        await call.message.answer("Пришлите файл: PDF или фото накладной. Бот распознаёт и покажет черновик.")
        await call.answer()
    
    logger.info(f"[TG] update done req={req} h=cb_act_upload")

@router.callback_query(F.data == "act_help")
async def cb_act_help(call: CallbackQuery):
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

