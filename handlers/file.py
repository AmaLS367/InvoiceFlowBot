import os
import time
import uuid
from pathlib import Path
from typing import Any, Dict

from aiogram import F, Router
from aiogram.types import BufferedInputFile, Message
from PIL import Image, ImageOps

from domain.drafts import InvoiceDraft
from handlers.deps import get_container, get_draft_service, get_invoice_service
from handlers.utils import (
    MAX_MSG,
    actions_kb,
    csv_bytes_from_items,
    format_invoice_full,
    format_invoice_header,
    format_invoice_items,
    send_chunked,
)
from ocr.engine.util import get_logger, save_file, set_request_id

router = Router()
logger = get_logger("ocr.engine")


# Note: /start, /help, and /gif handlers are now in handlers/commands_common.py
# This file only handles file uploads (documents and photos)


async def _process_file_and_create_draft(
    message: Message,
    file_path: str,
    container: Any,
    invoice_service: Any,
    draft_service: Any,
) -> None:
    """Common logic for processing file and creating draft."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext in {".heic", ".heif", ".webp"}:
        try:
            im = Image.open(file_path).convert("RGB")
            new_path = file_path.rsplit(".", 1)[0] + ".jpg"
            im.save(new_path, format="JPEG", quality=95)
            file_path = new_path
        except Exception as e:
            logger.exception(f"[TG] Failed to convert {ext} file to JPEG: {e}")
            await message.answer(
                "Не удалось обработать файл. Попробуйте другой формат (PDF, JPG, PNG)."
            )
            return

    if not file_path.lower().endswith(".pdf"):
        try:
            img: Image.Image = Image.open(file_path)
            img = ImageOps.exif_transpose(img).convert("RGB")
            ext = Path(file_path).suffix.lower()
            new_path = (
                file_path
                if ext in {".jpg", ".jpeg", ".png"}
                else str(Path(file_path).with_suffix(".jpg"))
            )
            img.save(new_path, format="JPEG", quality=95, optimize=True)
            file_path = new_path
        except Exception as e:
            logger.exception(f"[TG] Failed to normalize image file: {e}")
            await message.answer("Не удалось обработать файл. Попробуйте другой формат.")
            return

    uid = message.from_user.id if message.from_user else 0
    await message.answer("📥 Получил файл. Распознаю…")

    try:
        invoice = await invoice_service.process_invoice_file(
            pdf_path=file_path, fast=True, max_pages=12
        )
    except Exception as e:
        logger.exception(f"[TG] OCR failed for file {file_path}: {e}")
        await message.answer("Сервис распознавания сейчас недоступен. Попробуйте чуть позже.")
        return

    # Build an invoice draft so the user can review and edit the parsed data before saving.
    try:
        draft = InvoiceDraft(
            invoice=invoice,
            path=file_path,
            raw_text="",
            comments=[],
        )
        await draft_service.set_current_draft(user_id=uid, draft=draft)
    except Exception as e:
        logger.exception(f"[TG] Failed to create draft for file {file_path}: {e}")
        await message.answer("Не удалось сохранить черновик. Повторите попытку позже.")
        return

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


async def handle_invoice_document(message: Message, data: Dict[str, Any]) -> None:
    """Handle invoice document upload."""
    req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    set_request_id(req)
    logger.info(f"[TG] update start req={req} h=handle_invoice_document")
    container = get_container(data)
    invoice_service = get_invoice_service(container)
    draft_service = get_draft_service(container)

    if not message.document:
        await message.answer("Не удалось получить файл.")
        return

    if message.bot is None:
        await message.answer("Ошибка: бот недоступен")
        return

    path = await save_file(message.document, message.bot)
    if path is None:
        await message.answer("Ошибка при сохранении файла")
        return

    await _process_file_and_create_draft(message, path, container, invoice_service, draft_service)
    logger.info(f"[TG] update done req={req} h=handle_invoice_document")


async def handle_invoice_photo(message: Message, data: Dict[str, Any]) -> None:
    """Handle invoice photo upload."""
    req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    set_request_id(req)
    logger.info(f"[TG] update start req={req} h=handle_invoice_photo")
    container = get_container(data)
    invoice_service = get_invoice_service(container)
    draft_service = get_draft_service(container)

    from aiogram.types import PhotoSize

    if not message.photo:
        await message.answer("Не удалось получить фото.")
        return

    # Get the largest photo
    photo: PhotoSize = message.photo[-1]

    if message.bot is None:
        await message.answer("Ошибка: бот недоступен")
        return

    path = await save_file(photo, message.bot)
    if path is None:
        await message.answer("Ошибка при сохранении файла")
        return

    await _process_file_and_create_draft(message, path, container, invoice_service, draft_service)
    logger.info(f"[TG] update done req={req} h=handle_invoice_photo")


# Register handlers on router
router.message.register(handle_invoice_document, F.document)
router.message.register(handle_invoice_photo, F.photo)
