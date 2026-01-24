"""
Command handlers for working with invoice drafts.
"""

import re
import time
import uuid
from datetime import date
from decimal import Decimal

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from backend.core.container import AppContainer
from backend.domain.invoices import InvoiceComment
from backend.handlers.deps import get_draft_service, get_invoice_service
from backend.handlers.fsm import EditInvoiceState
from backend.handlers.utils import format_invoice_full, format_invoice_header
from backend.ocr.engine.util import get_logger, set_request_id
from backend.storage.db import to_iso

logger = get_logger("ocr.engine")


def _parse_date_str(date_str: str) -> date | None:
    """Parse date string to date object."""
    if not date_str:
        return None
    try:
        return date.fromisoformat(date_str)
    except (ValueError, TypeError):
        iso = to_iso(date_str)
        if iso:
            try:
                return date.fromisoformat(iso)
            except (ValueError, TypeError):
                pass
    return None


def setup(router: Router) -> None:
    """Register draft-related command handlers."""

    @router.message(F.text == "/show")
    async def cmd_show(message: Message, container: AppContainer) -> None:
        req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
        set_request_id(req)
        logger.info(f"[TG] update start req={req} h=cmd_show")
        draft_service = get_draft_service(container)
        uid = message.from_user.id if message.from_user else 0
        draft = await draft_service.get_current_draft(uid)
        if draft is None:
            await message.answer("Нет черновика. Пришлите документ.")
            return

        invoice = draft.invoice
        full_text = format_invoice_full(invoice)
        await message.answer(full_text if len(full_text) < 3900 else format_invoice_header(invoice))
        logger.info(f"[TG] update done req={req} h=cmd_show")

    @router.message(F.reply_to_message)
    async def on_force_reply(
        message: Message,
        state: FSMContext,
        container: AppContainer,
    ) -> None:
        req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
        set_request_id(req)
        logger.info(f"[TG] update start req={req} h=on_force_reply")
        draft_service = get_draft_service(container)
        uid = message.from_user.id if message.from_user else 0

        current_state = await state.get_state()

        if current_state == EditInvoiceState.waiting_for_comment:
            draft = await draft_service.get_current_draft(uid)
            if draft is None:
                await message.answer("Нет черновика. Загрузите документ.")
                await state.clear()
                return
            text = (message.text or "").strip()
            if not text:
                await message.answer("Пустой комментарий игнорирован.")
            else:
                draft.comments.append(text)
                await draft_service.set_current_draft(uid, draft)
                await message.answer("Комментарий добавлен.")
            await state.clear()
            logger.info(f"[TG] update done req={req} h=on_force_reply_comment")
            return

        if current_state == EditInvoiceState.waiting_for_field_value:
            state_data = await state.get_data()
            edit_config = state_data.get("edit_config") or {}
            kind = edit_config.get("kind")

            draft = await draft_service.get_current_draft(uid)
            if draft is None:
                await message.answer("Нет черновика. Загрузите документ.")
                await state.clear()
                return

            invoice = draft.invoice
            if message.text is not None:
                val = message.text.strip()

            if kind == "header":
                k = edit_config.get("key")
                header = invoice.header
                if k == "supplier":
                    header.supplier_name = val
                elif k == "client":
                    header.customer_name = val
                elif k == "date":
                    parsed_date = _parse_date_str(val)
                    header.invoice_date = parsed_date
                elif k == "doc_number":
                    header.invoice_number = val
                elif k == "total_sum":
                    try:
                        header.total_amount = Decimal(str(val.replace(",", ".")))
                        ok = True
                    except (ValueError, TypeError, Exception):
                        ok = False
                    await message.answer(
                        'Итого обновлено. Нажмите кнопку "Сохранить" или введите команду /save чтобы сохранить в БД.'
                        if ok
                        else "Итого обновлено как текст (не число)."
                    )
                    await draft_service.set_current_draft(uid, draft)
                    await state.clear()
                    return
                await message.answer(
                    'Поле обновлено. Нажмите кнопку "Сохранить" или введите команду /save чтобы сохранить в БД.'
                )
            elif kind == "item":
                idx_raw = edit_config.get("idx")
                if not isinstance(idx_raw, int):
                    await message.answer("Индекс не указан.")
                    await state.clear()
                    return
                idx = idx_raw
                items = invoice.items
                if not (1 <= idx <= len(items)):
                    await message.answer("Индекс вне диапазона.")
                    await state.clear()
                    return
                key = edit_config.get("key")
                item = items[idx - 1]
                if key == "name":
                    item.description = val
                elif key == "code":
                    item.sku = val
                elif key == "qty":
                    try:
                        item.quantity = Decimal(str(val.replace(",", ".")))
                    except (ValueError, TypeError, Exception):
                        await message.answer("Не число. Повторите.")
                        return
                elif key == "price":
                    try:
                        item.unit_price = Decimal(str(val.replace(",", ".")))
                    except (ValueError, TypeError, Exception):
                        await message.answer("Не число. Повторите.")
                        return
                elif key == "total":
                    try:
                        item.line_total = Decimal(str(val.replace(",", ".")))
                    except (ValueError, TypeError, Exception):
                        await message.answer("Не число. Повторите.")
                        return
                await message.answer(
                    'Обновлено. Нажмите кнопку "Сохранить" или введите команду /save чтобы сохранить в БД.'
                )

            await draft_service.set_current_draft(uid, draft)
            await state.clear()
            logger.info(f"[TG] update done req={req} h=on_force_reply")
            return

        logger.info(f"[TG] update done req={req} h=on_force_reply (no matching state)")

    @router.message(F.text.regexp(r"^/comment(\s|$)"))
    async def cmd_comment(message: Message, container: AppContainer) -> None:
        req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
        set_request_id(req)
        logger.info(f"[TG] update start req={req} h=cmd_comment")
        draft_service = get_draft_service(container)
        uid = message.from_user.id if message.from_user else 0
        draft = await draft_service.get_current_draft(uid)
        if draft is None:
            await message.answer("Нет черновика. Загрузите документ.")
            return
        if message.text is not None and " " in message.text:
            text = message.text.split(" ", 1)[1].strip() if " " in message.text else ""
            if not text:
                await message.answer("Формат: /comment ваш текст")
                return
        draft.comments.append(text)
        await draft_service.set_current_draft(uid, draft)
        await message.answer("Комментарий добавлен. /save чтобы сохранить в БД.")
        logger.info(f"[TG] update done req={req} h=cmd_comment")

    @router.message(F.text == "/save")
    async def cmd_save(message: Message, container: AppContainer) -> None:
        req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
        set_request_id(req)
        logger.info(f"[TG] update start req={req} h=cmd_save")
        invoice_service = get_invoice_service(container)
        draft_service = get_draft_service(container)
        uid = message.from_user.id if message.from_user else 0
        draft = await draft_service.get_current_draft(uid)
        if draft is None:
            await message.answer("Нет черновика.")
            return

        invoice = draft.invoice
        comments = draft.comments

        # Auto-comment for sum mismatch
        header_sum = (
            float(invoice.header.total_amount) if invoice.header.total_amount is not None else 0.0
        )
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
            existing_messages = [c.message for c in invoice.comments]
            if auto_text not in existing_messages:
                invoice.comments.append(InvoiceComment(message=auto_text))

        # Add text comments
        for comment_text in comments:
            if isinstance(comment_text, str):
                invoice.comments.append(InvoiceComment(message=comment_text))

        inv_id = await invoice_service.save_invoice(invoice, user_id=uid)
        await draft_service.clear_current_draft(uid)
        await message.answer(f"Сохранено в БД. ID счета: {inv_id}")
        logger.info(f"[TG] update done req={req} h=cmd_save")

    @router.message(F.text.regexp(r"^/edit(\s|$)"))
    async def cmd_edit_legacy(message: Message, container: AppContainer) -> None:
        req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
        set_request_id(req)
        logger.info(f"[TG] update start req={req} h=cmd_edit_legacy")
        draft_service = get_draft_service(container)
        uid = message.from_user.id if message.from_user else 0
        draft = await draft_service.get_current_draft(uid)
        if draft is None:
            await message.answer("Нет черновика. Загрузите документ.")
            return
        if message.text is None:
            await message.answer(
                "Формат: /edit supplier=... client=... date=YYYY-MM-DD doc=... total=123.45"
            )
            return
        args = message.text.split(" ", 1)
        if len(args) < 2:
            await message.answer(
                "Формат: /edit supplier=... client=... date=YYYY-MM-DD doc=... total=123.45"
            )
            return

        invoice = draft.invoice
        for part in re.split(r"[;,]\s*|\s{2,}", args[1].strip()):
            if "=" in part:
                k, v = part.split("=", 1)
                k = k.strip().lower()
                header = invoice.header
                if k in ("supplier", "поставщик"):
                    header.supplier_name = v.strip()
                elif k in ("client", "клиент"):
                    header.customer_name = v.strip()
                elif k in ("date", "дата"):
                    header.invoice_date = _parse_date_str(v.strip())
                elif k in ("doc", "number", "номер", "doc_number"):
                    header.invoice_number = v.strip()
                elif k in ("total", "итого", "sum", "total_sum"):
                    try:
                        header.total_amount = Decimal(str(v.replace(",", ".")))
                    except (ValueError, TypeError):
                        pass

        await draft_service.set_current_draft(uid, draft)
        await message.answer("Ок. Поля обновлены. /show для проверки или /save для сохранения.")
        logger.info(f"[TG] update done req={req} h=cmd_edit_legacy")

    @router.message(F.text.regexp(r"^/edititem(\s|$)"))
    async def cmd_edititem_legacy(message: Message, container: AppContainer) -> None:
        req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
        set_request_id(req)
        logger.info(f"[TG] update start req={req} h=cmd_edititem_legacy")
        draft_service = get_draft_service(container)
        uid = message.from_user.id if message.from_user else 0

        draft = await draft_service.get_current_draft(uid)
        if draft is None:
            await message.answer("Нет черновика. Загрузите документ.")
            return

        if message.text is None:
            await message.answer("Формат: /edititem <index> name=... qty=... price=... total=...")
            return
        args = message.text.split(" ", 2)

        if len(args) < 3:
            await message.answer("Формат: /edititem <index> name=... qty=... price=... total=...")
            return

        try:
            idx = int(args[1])
        except (ValueError, TypeError):
            await message.answer("Неверный индекс.")
            return

        invoice = draft.invoice
        items = invoice.items
        if idx < 1 or idx > len(items):
            await message.answer("Индекс вне диапазона.")
            return

        item = items[idx - 1]
        updates = args[2]
        for part in re.split(r"[;,]\s*|\s{2,}", updates.strip()):
            if "=" in part:
                k, v = part.split("=", 1)
                k = k.strip().lower()
                if k == "name":
                    item.description = v.strip()
                elif k == "code":
                    item.sku = v.strip()
                elif k == "qty":
                    try:
                        item.quantity = Decimal(str(v.replace(",", ".")))
                    except (ValueError, TypeError):
                        pass
                elif k == "price":
                    try:
                        item.unit_price = Decimal(str(v.replace(",", ".")))
                    except (ValueError, TypeError):
                        pass
                elif k == "total":
                    try:
                        item.line_total = Decimal(str(v.replace(",", ".")))
                    except (ValueError, TypeError):
                        pass
        await draft_service.set_current_draft(uid, draft)
        await message.answer("Позиция обновлена. /show для проверки, /save для сохранения.")
        logger.info(f"[TG] update done req={req} h=cmd_edititem_legacy")
