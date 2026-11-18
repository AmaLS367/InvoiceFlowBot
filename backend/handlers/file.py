import os
import time
import uuid
from pathlib import Path
from typing import Any

from aiogram import F, Router
from aiogram.types import BufferedInputFile, Message
from PIL import Image, ImageOps

from backend.core.container import AppContainer
from backend.domain.drafts import InvoiceDraft
from backend.handlers import texts
from backend.handlers.deps import get_draft_service, get_invoice_service
from backend.handlers.utils import (
    MAX_MSG,
    actions_kb,
    csv_bytes_from_items,
    format_invoice_full,
    format_invoice_header,
    format_invoice_items,
    format_ocr_review,
    send_chunked,
)
from backend.ocr.engine.util import get_logger, save_file, set_request_id
from backend.services.invoice_service import DEFAULT_MAX_OCR_PAGES, EmptyOcrResultError

router = Router()
logger = get_logger("ocr.engine")

# Max number of items to render inline before forcing CSV export.
MAX_INLINE_ITEMS = 60

# Max total length of items text before preferring CSV (keep a safe margin from Telegram limit).
MAX_ITEMS_TEXT_LENGTH = MAX_MSG * 2


async def _process_file_and_create_draft(
    message: Message,
    file_path: str,
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
            await message.answer(texts.FILE_PROCESSING_FAILED_WITH_FORMATS)
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
            await message.answer(texts.FILE_PROCESSING_FAILED)
            return

    uid = message.from_user.id if message.from_user else 0
    logger.info(
        "[TG] processing uploaded file user_id=%s path=%s ext=%s",
        uid,
        file_path,
        Path(file_path).suffix.lower(),
    )
    await message.answer(texts.OCR_IN_PROGRESS)

    try:
        invoice = await invoice_service.process_invoice_file(
            pdf_path=file_path,
            fast=True,
            max_pages=DEFAULT_MAX_OCR_PAGES,
        )
        logger.info(
            "[TG] OCR result user_id=%s path=%s doc=%r supplier=%r client=%r date=%r total=%r items=%s",
            uid,
            file_path,
            invoice.header.invoice_number,
            invoice.header.supplier_name,
            invoice.header.customer_name,
            invoice.header.invoice_date,
            invoice.header.total_amount,
            len(invoice.items),
        )
    except EmptyOcrResultError as e:
        logger.warning(f"[TG] OCR empty result for file {file_path}: {e}")
        await message.answer(texts.OCR_EMPTY_RESULT)
        return
    except Exception as e:
        logger.exception(f"[TG] OCR failed for file {file_path}: {e}")
        await message.answer(texts.OCR_UNAVAILABLE)
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
        await message.answer(texts.DRAFT_SAVE_FAILED)
        return

    full_text = format_invoice_full(invoice)

    if len(full_text) <= MAX_MSG:
        await message.answer(full_text, reply_markup=actions_kb())
    else:
        head_text = format_invoice_header(invoice)
        items_text = format_invoice_items(invoice.items)
        await message.answer(head_text, reply_markup=actions_kb())
        if len(invoice.items) > MAX_INLINE_ITEMS or len(items_text) > MAX_ITEMS_TEXT_LENGTH:
            await message.answer(texts.TABLE_TOO_LONG_SEND_CSV)
            await message.answer_document(
                BufferedInputFile(csv_bytes_from_items(invoice.items), filename="invoice_items.csv")
            )
        await send_chunked(message, items_text)

    review_text = format_ocr_review(invoice)
    if review_text:
        await send_chunked(message, review_text)


async def handle_invoice_document(message: Message, container: AppContainer) -> None:
    """Handle invoice document upload."""
    req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    set_request_id(req)
    logger.info(f"[TG] update start req={req} h=handle_invoice_document")
    invoice_service = get_invoice_service(container)
    draft_service = get_draft_service(container)

    if not message.document:
        await message.answer(texts.FILE_FETCH_FAILED)
        return

    if message.bot is None:
        await message.answer(texts.BOT_UNAVAILABLE)
        return

    logger.info(
        "[TG] document received user_id=%s file_id=%s file_name=%s mime=%s",
        message.from_user.id if message.from_user else 0,
        message.document.file_id,
        message.document.file_name,
        message.document.mime_type,
    )

    path = await save_file(message.document, message.bot)
    if path is None:
        await message.answer(texts.FILE_SAVE_FAILED)
        return

    await _process_file_and_create_draft(message, path, invoice_service, draft_service)
    logger.info(f"[TG] update done req={req} h=handle_invoice_document")


async def handle_invoice_photo(message: Message, container: AppContainer) -> None:
    """Handle invoice photo upload."""
    req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    set_request_id(req)
    logger.info(f"[TG] update start req={req} h=handle_invoice_photo")
    invoice_service = get_invoice_service(container)
    draft_service = get_draft_service(container)

    from aiogram.types import PhotoSize

    if not message.photo:
        await message.answer(texts.PHOTO_FETCH_FAILED)
        return

    # Get the largest photo
    photo: PhotoSize = message.photo[-1]

    logger.info(
        "[TG] photo received user_id=%s file_id=%s width=%s height=%s",
        message.from_user.id if message.from_user else 0,
        photo.file_id,
        photo.width,
        photo.height,
    )

    if message.bot is None:
        await message.answer(texts.BOT_UNAVAILABLE)
        return

    path = await save_file(photo, message.bot)
    if path is None:
        await message.answer(texts.FILE_SAVE_FAILED)
        return

    await _process_file_and_create_draft(message, path, invoice_service, draft_service)
    logger.info(f"[TG] update done req={req} h=handle_invoice_photo")


# Register handlers on router
router.message.register(handle_invoice_document, F.document)
router.message.register(handle_invoice_photo, F.photo)
