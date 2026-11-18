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
from backend.handlers import texts
from backend.handlers.deps import get_draft_service, get_invoice_service
from backend.handlers.fsm import EditInvoiceState
from backend.handlers.utils import actions_kb, format_invoice_full, format_invoice_header
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


def _state_matches(current_state: object, expected_state: object) -> bool:
    expected_value = getattr(expected_state, "state", None)
    return current_state == expected_state or (
        isinstance(current_state, str)
        and expected_value is not None
        and current_state == expected_value
    )


async def handle_force_reply(
    message: Message,
    state: FSMContext,
    container: AppContainer,
) -> bool:
    """Handle draft-related force replies. Returns True when the reply was consumed."""
    req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    set_request_id(req)
    logger.info(f"[TG] update start req={req} h=on_force_reply")
    draft_service = get_draft_service(container)
    uid = message.from_user.id if message.from_user else 0

    current_state = await state.get_state()

    if _state_matches(current_state, EditInvoiceState.waiting_for_comment):
        draft = await draft_service.get_current_draft(uid)
        if draft is None:
            await message.answer(texts.t("NO_DRAFT_UPLOAD_DOCUMENT"))
            await state.clear()
            return True
        text = (message.text or "").strip()
        if not text:
            await message.answer(texts.t("COMMENT_EMPTY_IGNORED"))
        else:
            draft.comments.append(text)
            await draft_service.set_current_draft(uid, draft)
            await message.answer(
                texts.t("COMMENT_ADDED_SAVE_HINT"),
                reply_markup=actions_kb(),
            )
        await state.clear()
        logger.info(f"[TG] update done req={req} h=on_force_reply_comment")
        return True

    if not _state_matches(current_state, EditInvoiceState.waiting_for_field_value):
        logger.info(f"[TG] update done req={req} h=on_force_reply (no matching state)")
        return False

    state_data = await state.get_data()
    edit_config = state_data.get("edit_config") or {}
    kind = edit_config.get("kind")

    draft = await draft_service.get_current_draft(uid)
    if draft is None:
        await message.answer(texts.t("NO_DRAFT_UPLOAD_DOCUMENT"))
        await state.clear()
        return True

    invoice = draft.invoice
    val = (message.text or "").strip()

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
                texts.t("TOTAL_UPDATED") if ok else texts.t("TOTAL_UPDATED_AS_TEXT")
            )
            await draft_service.set_current_draft(uid, draft)
            await state.clear()
            return True
        await message.answer(texts.t("FIELD_UPDATED"))
    elif kind == "item":
        idx_raw = edit_config.get("idx")
        if not isinstance(idx_raw, int):
            await message.answer(texts.t("INDEX_MISSING"))
            await state.clear()
            return True
        idx = idx_raw
        items = invoice.items
        if not (1 <= idx <= len(items)):
            await message.answer(texts.t("INDEX_OUT_OF_RANGE"))
            await state.clear()
            return True
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
                await message.answer(texts.t("NOT_A_NUMBER_RETRY"))
                return True
        elif key == "price":
            try:
                item.unit_price = Decimal(str(val.replace(",", ".")))
            except (ValueError, TypeError, Exception):
                await message.answer(texts.t("NOT_A_NUMBER_RETRY"))
                return True
        elif key == "total":
            try:
                item.line_total = Decimal(str(val.replace(",", ".")))
            except (ValueError, TypeError, Exception):
                await message.answer(texts.t("NOT_A_NUMBER_RETRY"))
                return True
        await message.answer(texts.t("ITEM_UPDATED"))

    await draft_service.set_current_draft(uid, draft)
    await state.clear()
    logger.info(f"[TG] update done req={req} h=on_force_reply")
    return True


def setup(router: Router, include_reply_handler: bool = True) -> None:
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
            await message.answer(texts.t("NO_DRAFT_SEND_DOCUMENT"))
            return

        invoice = draft.invoice
        full_text = format_invoice_full(invoice, extra_comments=draft.comments)
        await message.answer(full_text if len(full_text) < 3900 else format_invoice_header(invoice))
        logger.info(f"[TG] update done req={req} h=cmd_show")

    if include_reply_handler:

        @router.message(F.reply_to_message)
        async def on_force_reply(
            message: Message,
            state: FSMContext,
            container: AppContainer,
        ) -> None:
            await handle_force_reply(message, state, container)

    @router.message(F.text.regexp(r"^/comment(\s|$)"))
    async def cmd_comment(message: Message, container: AppContainer) -> None:
        req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
        set_request_id(req)
        logger.info(f"[TG] update start req={req} h=cmd_comment")
        draft_service = get_draft_service(container)
        uid = message.from_user.id if message.from_user else 0
        draft = await draft_service.get_current_draft(uid)
        if draft is None:
            await message.answer(texts.t("NO_DRAFT_UPLOAD_DOCUMENT"))
            return
        if message.text is None or " " not in message.text:
            await message.answer(texts.t("COMMENT_USAGE"))
            return
        text = message.text.split(" ", 1)[1].strip()
        if not text:
            await message.answer(texts.t("COMMENT_USAGE"))
            return
        draft.comments.append(text)
        await draft_service.set_current_draft(uid, draft)
        await message.answer(
            texts.t("COMMENT_ADDED_SAVE_HINT"),
            reply_markup=actions_kb(),
        )
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
            await message.answer(texts.t("NO_DRAFT_SHORT"))
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
            doc_number = invoice.header.invoice_number or texts.PLACEHOLDER
            supplier = invoice.header.supplier_name or texts.PLACEHOLDER
            auto_text = texts.auto_sum_mismatch_comment(
                sum_items=sum_items,
                header_sum=header_sum,
                diff=diff,
                doc_number=doc_number,
                supplier=supplier,
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
        await message.answer(texts.save_success(inv_id))
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
            await message.answer(texts.t("NO_DRAFT_UPLOAD_DOCUMENT"))
            return
        if message.text is None:
            await message.answer(texts.t("EDIT_USAGE"))
            return
        args = message.text.split(" ", 1)
        if len(args) < 2:
            await message.answer(texts.t("EDIT_USAGE"))
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
        await message.answer(texts.t("HEADER_UPDATED"))
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
            await message.answer(texts.t("NO_DRAFT_UPLOAD_DOCUMENT"))
            return

        if message.text is None:
            await message.answer(texts.t("EDITITEM_USAGE"))
            return
        args = message.text.split(" ", 2)

        if len(args) < 3:
            await message.answer(texts.t("EDITITEM_USAGE"))
            return

        try:
            idx = int(args[1])
        except (ValueError, TypeError):
            await message.answer(texts.t("INDEX_INVALID"))
            return

        invoice = draft.invoice
        items = invoice.items
        if idx < 1 or idx > len(items):
            await message.answer(texts.t("INDEX_OUT_OF_RANGE"))
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
        await message.answer(texts.t("LINE_UPDATED"))
        logger.info(f"[TG] update done req={req} h=cmd_edititem_legacy")
