"""
Miscellaneous callback handlers.
"""

import time
import uuid
from typing import Any, Dict

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, ForceReply

from handlers.fsm import InvoicesPeriodState
from ocr.engine.util import get_logger, set_request_id

logger = get_logger("ocr.engine")


def setup(router: Router) -> None:
    """Register miscellaneous callback handlers."""

    @router.callback_query(F.data == "act_period")
    async def cb_act_period(call: CallbackQuery, state: FSMContext, data: Dict[str, Any]) -> None:
        """Handle period action callback - prompt for date range input."""
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

    @router.callback_query(F.data == "act_upload")
    async def cb_act_upload(call: CallbackQuery, data: Dict[str, Any]) -> None:
        """Handle upload action callback - prompt for file upload."""
        req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
        set_request_id(req)
        logger.info(f"[TG] update start req={req} h=cb_act_upload")

        if call.message is not None:
            await call.message.answer(
                "Пришлите файл: PDF или фото накладной. Бот распознаёт и покажет черновик."
            )
            await call.answer()

        logger.info(f"[TG] update done req={req} h=cb_act_upload")

    @router.callback_query(F.data == "act_help")
    async def cb_act_help(call: CallbackQuery, data: Dict[str, Any]) -> None:
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
