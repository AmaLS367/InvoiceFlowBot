"""
Command handlers for working with invoices (listing, filtering, etc.).
"""

import time
import uuid
from datetime import date

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, ForceReply, Message

from core.container import AppContainer
from handlers.callback_registry import CallbackAction
from handlers.deps import get_invoice_service
from handlers.fsm import InvoicesPeriodState
from handlers.utils import format_money
from ocr.engine.util import get_logger, set_request_id
from storage.db import to_iso

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


async def cmd_invoices(message: Message, container: AppContainer) -> None:
    """Handle /invoices command."""
    req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    set_request_id(req)
    logger.info(f"[TG] update start req={req} h=cmd_invoices")
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
        supplier = parts[3].split("=", 1)[1]

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
        invoice_date_str = (
            invoice.header.invoice_date.isoformat() if invoice.header.invoice_date else "—"
        )
        invoice_total = (
            float(invoice.header.total_amount) if invoice.header.total_amount is not None else 0.0
        )
        total += invoice_total
        items_count_val = len(invoice.items)
        lines.append(
            f"  {invoice_date_str}  {invoice.header.invoice_number or '—'}  "
            f"{invoice.header.supplier_name or '—'}  = {format_money(invoice_total)}  "
            f"(items: {items_count_val})"
        )
    head = f"Счета с {f_str} по {t_str}" + (
        f" | Поставщик содержит: {supplier}" if supplier else ""
    )
    text = head + "\n" + "\n".join(lines[:150]) + f"\n—\nИтого суммарно: {format_money(total)}"
    await message.answer(
        text if len(text) < 3900 else (head + "\nСлишком много строк. Уточните фильтр.")
    )
    logger.info(f"[TG] update done req={req} h=cmd_invoices")


def setup(router: Router) -> None:
    """Register invoice-related command handlers."""
    router.message.register(cmd_invoices, F.text.regexp(r"^/invoices\s"))

    @router.message(F.reply_to_message)
    async def on_force_reply_invoices(
        message: Message,
        state: FSMContext,
        container: AppContainer,
    ) -> None:
        req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
        set_request_id(req)
        logger.info(f"[TG] update start req={req} h=on_force_reply_invoices")
        invoice_service = get_invoice_service(container)

        current_state = await state.get_state()

        if current_state == InvoicesPeriodState.waiting_for_from_date:
            if message.text is not None:
                val = message.text.strip()
                iso = to_iso(val) or val
                state_data = await state.get_data()
                period = state_data.get("period") or {}
                period["from"] = iso
                await state.update_data({"period": period})
                await state.set_state(InvoicesPeriodState.waiting_for_to_date)
                await message.answer(
                    "По дату (YYYY-MM-DD):", reply_markup=ForceReply(selective=True)
                )
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
                await message.answer(
                    "Фильтр по поставщику (опционально). Введите текст или «-» чтобы пропустить:",
                    reply_markup=ForceReply(selective=True),
                )
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
                    invoice_date_str = (
                        invoice.header.invoice_date.isoformat()
                        if invoice.header.invoice_date
                        else "—"
                    )
                    invoice_total = (
                        float(invoice.header.total_amount)
                        if invoice.header.total_amount is not None
                        else 0.0
                    )
                    total += invoice_total
                    items_count_val = len(invoice.items)
                    lines.append(
                        f"  {invoice_date_str}  {invoice.header.invoice_number or '—'}  "
                        f"{invoice.header.supplier_name or '—'}  = {format_money(invoice_total)}  "
                        f"(items: {items_count_val})"
                    )
                head = f"Счета с {f_str} по {t_str}" + (
                    f" | Поставщик содержит: {supplier}" if supplier else ""
                )
                text = (
                    head
                    + "\n"
                    + "\n".join(lines[:150])
                    + f"\n—\nИтого суммарно: {format_money(total)}"
                )
                await message.answer(
                    text if len(text) < 3900 else (head + "\nСлишком много строк. Уточните фильтр.")
                )
                return

    @router.callback_query(F.data == CallbackAction.PERIOD.value)
    async def cb_act_period(call: CallbackQuery, state: FSMContext) -> None:
        req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
        set_request_id(req)
        logger.info(f"[TG] update start req={req} h=cb_act_period")

        await state.set_state(InvoicesPeriodState.waiting_for_from_date)
        await state.update_data({"period": {}})
        if call.message is not None:
            await call.message.answer(
                "С даты (YYYY-MM-DD):", reply_markup=ForceReply(selective=True)
            )
            await call.answer()
        logger.info(f"[TG] update done req={req} h=cb_act_period")
