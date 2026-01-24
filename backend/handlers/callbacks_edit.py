"""
Callback handlers for invoice editing.
"""

import time
import uuid

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, ForceReply

from core.container import AppContainer
from domain.invoices import InvoiceComment
from handlers.callback_registry import (
    HEADER_PREFIX,
    ITEM_FIELD_PREFIX,
    ITEM_PICK_PREFIX,
    ITEMS_PAGE_PREFIX,
    CallbackAction,
)
from handlers.deps import get_draft_service, get_invoice_service
from handlers.fsm import EditInvoiceState
from handlers.utils import (
    format_invoice_header,
    format_money,
    header_kb,
    item_fields_kb,
    items_index_kb,
)
from ocr.engine.util import get_logger, set_request_id

logger = get_logger("ocr.engine")


def setup(router: Router) -> None:
    """Register edit-related callback handlers."""

    @router.callback_query(F.data == CallbackAction.EDIT.value)
    async def cb_act_edit(call: CallbackQuery, container: AppContainer) -> None:
        """Handle edit action callback - show header editing options."""
        req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
        set_request_id(req)
        logger.info(f"[TG] update start req={req} h=cb_act_edit")
        draft_service = get_draft_service(container)
        uid = call.from_user.id
        draft = await draft_service.get_current_draft(uid)
        if draft is None:
            if call.message is not None:
                await call.message.answer("Нет черновика. Пришлите документ.")
                await call.answer()
            return

        invoice = draft.invoice
        head_text = format_invoice_header(invoice)

        if call.message is not None:
            await call.message.answer(
                head_text + "\nВыберите поле для редактирования:", reply_markup=header_kb()
            )
            await call.answer()
        logger.info(f"[TG] update done req={req} h=cb_act_edit")

    @router.callback_query(F.data.startswith(HEADER_PREFIX))
    async def cb_hed_field(
        call: CallbackQuery,
        state: FSMContext,
        container: AppContainer,
    ) -> None:
        """Handle header field selection for editing."""
        req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
        set_request_id(req)
        logger.info(f"[TG] update start req={req} h=cb_hed_field")
        draft_service = get_draft_service(container)
        uid = call.from_user.id
        draft = await draft_service.get_current_draft(uid)
        if draft is None:
            await call.answer()
            return

        if call.data is not None:
            field = call.data.split(":", 1)[1]
            nice = {
                "supplier": "Поставщик",
                "client": "Клиент",
                "date": "Дата",
                "doc_number": "Номер",
                "total_sum": "Итого",
            }[field]
        await state.set_state(EditInvoiceState.waiting_for_field_value)
        await state.update_data(
            {
                "edit_config": {
                    "kind": "header",
                    "key": field,
                }
            }
        )
        if call.message is not None:
            await call.message.answer(
                f"Введите новое значение для «{nice}»:", reply_markup=ForceReply(selective=True)
            )
            await call.answer()
        logger.info(f"[TG] update done req={req} h=cb_hed_field")

    @router.callback_query(F.data == CallbackAction.ITEMS.value)
    async def cb_act_items(call: CallbackQuery, container: AppContainer) -> None:
        """Handle items action callback - show items list for editing."""
        req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
        set_request_id(req)
        logger.info(f"[TG] update start req={req} h=cb_act_items")
        draft_service = get_draft_service(container)
        uid = call.from_user.id
        draft = await draft_service.get_current_draft(uid)
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
            await call.message.answer(
                f"Выберите позицию для редактирования (всего: {n}):",
                reply_markup=items_index_kb(n, 1),
            )
            await call.answer()
        logger.info(f"[TG] update done req={req} h=cb_act_items")

    @router.callback_query(F.data.startswith(ITEMS_PAGE_PREFIX + ":"))
    async def cb_items_page(call: CallbackQuery, container: AppContainer) -> None:
        """Handle items pagination callback."""
        req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
        set_request_id(req)
        logger.info(f"[TG] update start req={req} h=cb_items_page")
        draft_service = get_draft_service(container)
        uid = call.from_user.id
        draft = await draft_service.get_current_draft(uid)
        if draft is None:
            await call.answer()
            return

        if call.data is not None:
            page = int(call.data.split(":")[1])
            invoice = draft.invoice
            n = len(invoice.items)

            if call.message is not None:
                from aiogram.types import Message

                if isinstance(call.message, Message):
                    await call.message.edit_reply_markup(reply_markup=items_index_kb(n, page))
                    await call.answer()
        logger.info(f"[TG] update done req={req} h=cb_items_page")

    @router.callback_query(F.data.startswith(ITEM_PICK_PREFIX + ":"))
    async def cb_item_pick(call: CallbackQuery, container: AppContainer) -> None:
        """Handle item selection callback - show item details for editing."""
        req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
        set_request_id(req)
        logger.info(f"[TG] update start req={req} h=cb_item_pick")
        draft_service = get_draft_service(container)
        uid = call.from_user.id
        draft = await draft_service.get_current_draft(uid)
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
        item = items[idx - 1]
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

    @router.callback_query(F.data.startswith(ITEM_FIELD_PREFIX + ":"))
    async def cb_itm_field(
        call: CallbackQuery,
        state: FSMContext,
    ) -> None:
        """Handle item field selection for editing."""
        req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
        set_request_id(req)
        logger.info(f"[TG] update start req={req} h=cb_itm_field")
        if call.data is None:
            await call.answer()
            return
        parts = call.data.split(":")
        idx = int(parts[1])
        key = parts[2]  # name/qty/price/total
        nice = {"name": "Название", "qty": "Кол-во", "price": "Цена", "total": "Сумма"}[key]
        await state.set_state(EditInvoiceState.waiting_for_field_value)
        await state.update_data(
            {
                "edit_config": {
                    "kind": "item",
                    "idx": idx,
                    "key": key,
                }
            }
        )
        if call.message is not None:
            await call.message.answer(
                f"Введите новое значение для «{nice}» у позиции #{idx}:",
                reply_markup=ForceReply(selective=True),
            )
            await call.answer()
        logger.info(f"[TG] update done req={req} h=cb_itm_field")

    @router.callback_query(F.data == CallbackAction.COMMENT.value)
    async def cb_act_comment(
        call: CallbackQuery,
        state: FSMContext,
        container: AppContainer,
    ) -> None:
        """Handle comment action callback - prompt for comment input."""
        req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
        set_request_id(req)
        logger.info(f"[TG] update start req={req} h=cb_act_comment")
        draft_service = get_draft_service(container)
        uid = call.from_user.id
        draft = await draft_service.get_current_draft(uid)
        if draft is None:
            if call.message is not None:
                await call.message.answer("Нет черновика. Пришлите документ.")
            await call.answer()
            return

        await state.set_state(EditInvoiceState.waiting_for_comment)
        await state.update_data(
            {
                "edit_config": {
                    "kind": "comment",
                }
            }
        )
        if call.message is not None:
            await call.message.answer(
                "Комментарий к счёту:", reply_markup=ForceReply(selective=True)
            )
        await call.answer()
        logger.info(f"[TG] update done req={req} h=cb_act_comment")

    @router.callback_query(F.data == CallbackAction.SAVE.value)
    async def cb_act_save(call: CallbackQuery, container: AppContainer) -> None:
        """Handle save action callback - save invoice to database."""
        req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
        set_request_id(req)
        logger.info(f"[TG] update start req={req} h=cb_act_save")
        invoice_service = get_invoice_service(container)
        draft_service = get_draft_service(container)
        uid = call.from_user.id
        draft = await draft_service.get_current_draft(uid)
        if draft is None:
            if call.message is not None:
                await call.message.answer("Нет черновика. Пришлите документ.")
            await call.answer()
            return

        invoice = draft.invoice
        comments = list(draft.comments)

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
            if auto_text not in comments:
                invoice.comments.append(InvoiceComment(message=auto_text))

        inv_id = await invoice_service.save_invoice(invoice, user_id=uid)
        await draft_service.clear_current_draft(uid)
        if call.message is not None:
            await call.message.answer(f"Сохранено в БД. ID счета: {inv_id}")
        await call.answer()
        logger.info(f"[TG] update done req={req} h=cb_act_save")
