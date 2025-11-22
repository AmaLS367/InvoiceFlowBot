from aiogram import Router, F
from aiogram.types import Message, BufferedInputFile

from handlers.state import CURRENT_PARSE
from handlers.utils import (
    format_invoice_full,
    format_invoice_header,
    format_invoice_items,
    csv_bytes_from_items,
    send_chunked,
    main_kb, actions_kb, MAX_MSG
)

from services.invoice_service import process_invoice_file, save_invoice
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
        try:
            im = Image.open(path).convert("RGB")
            new_path = path.rsplit(".", 1)[0] + ".jpg"
            im.save(new_path, format="JPEG", quality=95)
            path = new_path
        except Exception as e:
            logger.exception(f"[TG] Failed to convert {ext} file to JPEG: {e}")
            await message.answer("Не удалось обработать файл. Попробуйте другой формат (PDF, JPG, PNG).")
            return
        
    # Normalize photo: EXIF rotation and convert to JPEG
    if not path.lower().endswith(".pdf"):
        try:
            img = Image.open(path)
            img = ImageOps.exif_transpose(img).convert("RGB")
            ext = Path(path).suffix.lower()
            new_path = path if ext in {".jpg", ".jpeg", ".png"} else str(Path(path).with_suffix(".jpg"))
            img.save(new_path, format="JPEG", quality=95, optimize=True)
            path = new_path
        except Exception as e:
            logger.exception(f"[TG] Failed to normalize image file: {e}")
            await message.answer("Не удалось обработать файл. Попробуйте другой формат.")
            return
    uid = message.from_user.id if message.from_user else 0
    await message.answer("📥 Получил файл. Распознаю…")

    try:
        invoice = process_invoice_file(pdf_path=path, fast=True, max_pages=12)
    except Exception as e:
        logger.exception(f"[TG] OCR failed for file {path}: {e}")
        await message.answer("Сервис распознавания сейчас недоступен. Попробуйте чуть позже.")
        return

    # Save draft in memory
    CURRENT_PARSE[uid] = {
        "invoice": invoice,
        "path": path,
        "raw_text": "",  # Not available from service layer
        "comments": []
    }

    full_text = format_invoice_full(invoice)

    if len(full_text) <= MAX_MSG:
        await message.answer(full_text, reply_markup=actions_kb())
    else:
        head_text = format_invoice_header(invoice)
        items_text = format_invoice_items(invoice.items)
        await message.answer(head_text, reply_markup=actions_kb())
        if len(invoice.items) > 60 or len(items_text) > MAX_MSG * 2:
            await message.answer("Таблица длинная, отправляю CSV.")
            await message.answer_document(
                BufferedInputFile(csv_bytes_from_items(invoice.items), filename="invoice_items.csv")
            )
        await send_chunked(message, items_text)
    logger.info(f"[TG] update done req={req} h=handle_doc_or_photo")

