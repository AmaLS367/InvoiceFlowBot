import re
import time
import uuid
from datetime import date
from decimal import Decimal
from typing import Any, Dict

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, ForceReply, Message

from domain.invoices import InvoiceComment
from handlers.deps import get_container, get_draft_service, get_invoice_service
from handlers.fsm import EditInvoiceState, InvoicesPeriodState
from handlers.utils import (
    format_invoice_full,
    format_invoice_header,
    format_money,
    main_kb,
)
from ocr.engine.util import get_logger, set_request_id
from storage.db import to_iso

router = Router()
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

@router.message(F.text == "/start")
async def cmd_start(message: Message, data: Dict[str, Any]) -> None:
    req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    set_request_id(req)
    logger.info(f"[TG] update start req={req} h=cmd_start")
    await message.answer(
        "Готов принять PDF/фото накладной и превратить в данные.\n"
        "Шаги: 1) пришлите файл, 2) проверьте/отредактируйте, "
        "3) сохраните в БД, 4) запрос по периоду.",
        reply_markup=main_kb()
    )
    logger.info(f"[TG] update done req={req} h=cmd_start")

@router.message(F.text == "/help")
async def cmd_help(message: Message, data: Dict[str, Any]) -> None:
    req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    set_request_id(req)
    logger.info(f"[TG] update start req={req} h=cmd_help")
    await message.answer(
        "Быстрые действия кнопками ниже.\n"
        "Команды для продвинутых: /show, /edit, /edititem, /comment, /save, /invoices.",
        reply_markup=main_kb()
    )
    logger.info(f"[TG] update done req={req} h=cmd_help")

@router.message(F.text == "/show")
async def cmd_show(message: Message, data: Dict[str, Any]) -> None:
    req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    set_request_id(req)
    logger.info(f"[TG] update start req={req} h=cmd_show")
    container = get_container(data)
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
    data: Dict[str, Any],
) -> None:
    req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    set_request_id(req)
    logger.info(f"[TG] update start req={req} h=on_force_reply")
    container = get_container(data)
    draft_service = get_draft_service(container)
    invoice_service = get_invoice_service(container)
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
    
    if current_state == InvoicesPeriodState.waiting_for_from_date:
        if message.text is not None:
            val = message.text.strip()
            iso = to_iso(val) or val
            state_data = await state.get_data()
            period = state_data.get("period") or {}
            period["from"] = iso
            await state.update_data({"period": period})
            await state.set_state(InvoicesPeriodState.waiting_for_to_date)
            await message.answer("По дату (YYYY-MM-DD):", reply_markup=ForceReply(selective=True))
            return

    if current_state == InvoicesPeriodState.waiting_for_to_date:
        if message.text is not None:
            val = message.text.strip()
            iso = to_iso(val) or val
            state_data = await state.get_data()
            period = state_data.get("period") or {}
            period["to"] = iso
            await state.update_data({"period": period})
            await state.set_state(InvoicesPeriodState.waiting_for_supplier)
            await message.answer("Фильтр по поставщику (опционально). Введите текст или «-» чтобы пропустить:",
                                 reply_markup=ForceReply(selective=True))
            return

    if current_state == InvoicesPeriodState.waiting_for_supplier:
        if message.text is not None:
            val = message.text.strip()
            supplier = None if val in ("", "-") else val
            state_data = await state.get_data()
            period = state_data.get("period") or {}
            f_str = period.get("from")
            t_str = period.get("to")
            await state.clear()

            if not f_str or not t_str:
                await message.answer("Не указаны даты. Повторите ввод периода.")
                return

            from_date = _parse_date_str(f_str)
            to_date = _parse_date_str(t_str)

            invoices = await invoice_service.list_invoices(
                from_date=from_date, to_date=to_date, supplier=supplier
            )
            if not invoices:
                await message.answer("Ничего не найдено.")
                return

            lines = []
            total = 0.0
            for invoice in invoices:
                invoice_date_str = invoice.header.invoice_date.isoformat() if invoice.header.invoice_date else "—"
                invoice_total = float(invoice.header.total_amount) if invoice.header.total_amount is not None else 0.0
                total += invoice_total
                items_count_val = len(invoice.items)
                lines.append(
                    f"  {invoice_date_str}  {invoice.header.invoice_number or '—'}  "
                    f"{invoice.header.supplier_name or '—'}  = {format_money(invoice_total)}  "
                    f"(items: {items_count_val})"
                )
            head = f"Счета с {f_str} по {t_str}" + (f" | Поставщик содержит: {supplier}" if supplier else "")
            text = head + "\n" + "\n".join(lines[:150]) + f"\n—\nИтого суммарно: {format_money(total)}"
            await message.answer(text if len(text) < 3900 else (head + "\nСлишком много строк. Уточните фильтр."))
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
                await message.answer('Итого обновлено. Нажмите кнопку "Сохранить" или введите команду /save чтобы сохранить в БД.' if ok else "Итого обновлено как текст (не число).")
                await draft_service.set_current_draft(uid, draft)
                await state.clear()
                return
            await message.answer('Поле обновлено. Нажмите кнопку "Сохранить" или введите команду /save чтобы сохранить в БД.')
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
            await message.answer('Обновлено. Нажмите кнопку "Сохранить" или введите команду /save чтобы сохранить в БД.')

        await draft_service.set_current_draft(uid, draft)
        await state.clear()
        logger.info(f"[TG] update done req={req} h=on_force_reply")
        return
    
    # If state is not one of the expected states, do nothing
    logger.info(f"[TG] update done req={req} h=on_force_reply (no matching state)")

@router.message(F.text.regexp(r"^/comment(\s|$)"))
async def cmd_comment(message: Message, data: Dict[str, Any]) -> None:
    req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    set_request_id(req)
    logger.info(f"[TG] update start req={req} h=cmd_comment")
    container = get_container(data)
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
async def cmd_save(message: Message, data: Dict[str, Any]) -> None:
    req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    set_request_id(req)
    logger.info(f"[TG] update start req={req} h=cmd_save")
    container = get_container(data)
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

@router.message(F.text.regexp(r"^/invoices\s"))
async def cmd_invoices(message: Message, data: Dict[str, Any]) -> None:
    req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    set_request_id(req)
    logger.info(f"[TG] update start req={req} h=cmd_invoices")
    container = get_container(data)
    invoice_service = get_invoice_service(container)
    if message.text is None:
        await message.answer("Формат: /invoices YYYY-MM-DD YYYY-MM-DD [supplier=текст]")
        return
    parts = message.text.split()
    if len(parts) < 3:
        await message.answer("Формат: /invoices YYYY-MM-DD YYYY-MM-DD [supplier=текст]")
        return
    f_str, t_str = parts[1], parts[2]
    supplier = None
    if len(parts) >= 4 and parts[3].lower().startswith("supplier="):
        supplier = parts[3].split("=",1)[1]

    from_date = _parse_date_str(f_str)
    to_date = _parse_date_str(t_str)

    invoices = await invoice_service.list_invoices(
        from_date=from_date, to_date=to_date, supplier=supplier
    )
    if not invoices:
        await message.answer("Ничего не найдено.")
        return
    
    lines = []
    total = 0.0
    for invoice in invoices:
        invoice_date_str = invoice.header.invoice_date.isoformat() if invoice.header.invoice_date else "—"
        invoice_total = float(invoice.header.total_amount) if invoice.header.total_amount is not None else 0.0
        total += invoice_total
        items_count_val = len(invoice.items)
        lines.append(
            f"  {invoice_date_str}  {invoice.header.invoice_number or '—'}  "
            f"{invoice.header.supplier_name or '—'}  = {format_money(invoice_total)}  "
            f"(items: {items_count_val})"
        )
    head = f"Счета с {f_str} по {t_str}" + (f" | Поставщик содержит: {supplier}" if supplier else "")
    text = head + "\n" + "\n".join(lines[:150]) + f"\n—\nИтого суммарно: {format_money(total)}"
    await message.answer(text if len(text) < 3900 else (head + "\nСлишком много строк. Уточните фильтр."))
    logger.info(f"[TG] update done req={req} h=cmd_invoices")

@router.message(F.text.regexp(r"^/edit(\s|$)"))
async def cmd_edit_legacy(message: Message, data: Dict[str, Any]) -> None:
    req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    set_request_id(req)
    logger.info(f"[TG] update start req={req} h=cmd_edit_legacy")
    container = get_container(data)
    draft_service = get_draft_service(container)
    uid = message.from_user.id if message.from_user else 0
    draft = await draft_service.get_current_draft(uid)
    if draft is None:
        await message.answer("Нет черновика. Загрузите документ.")
        return
    if message.text is None:
        await message.answer("Формат: /edit supplier=... client=... date=YYYY-MM-DD doc=... total=123.45")
        return
    args = message.text.split(" ", 1)
    if len(args) < 2:
        await message.answer("Формат: /edit supplier=... client=... date=YYYY-MM-DD doc=... total=123.45")
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
async def cmd_edititem_legacy(message: Message, data: Dict[str, Any]) -> None:
    req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    set_request_id(req)
    logger.info(f"[TG] update start req={req} h=cmd_edititem_legacy")
    container = get_container(data)
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

    item = items[idx-1]
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

@router.callback_query(F.data == "act_period")
async def cb_act_period(call: CallbackQuery, state: FSMContext, data: Dict[str, Any]) -> None:
    req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    set_request_id(req)
    logger.info(f"[TG] update start req={req} h=cb_act_period")

    await state.set_state(InvoicesPeriodState.waiting_for_from_date)
    await state.update_data({"period": {}})
    if call.message is not None:
        await call.message.answer("С даты (YYYY-MM-DD):", reply_markup=ForceReply(selective=True))
        await call.answer()
    logger.info(f"[TG] update done req={req} h=cb_act_period")

