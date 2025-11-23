"""
Common command handlers: /start, /help, etc.
"""
import time
import uuid
from typing import Any, Dict

from aiogram import F, Router
from aiogram.types import Message

from handlers.utils import main_kb
from ocr.engine.util import get_logger, set_request_id

logger = get_logger("ocr.engine")


def setup(router: Router) -> None:
    """Register common command handlers."""

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

