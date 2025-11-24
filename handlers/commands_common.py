"""
Common command handlers: /start, /help, etc.
"""

import uuid

from aiogram import F, Router
from aiogram.types import Message

from handlers.utils import main_kb
from ocr.engine.util import get_logger, set_request_id

logger = get_logger("ocr.engine")


async def cmd_start(message: Message) -> None:
    req = str(uuid.uuid4())
    set_request_id(req)
    logger.info(f"[TG] update start req={req} h=cmd_start")
    await message.answer(
        "Привет! Это бот для обработки инвойсов. Загрузите счет и бот распознает его.",
        reply_markup=main_kb(),
    )
    logger.info(f"[TG] update done req={req} h=cmd_start")


async def cmd_help(message: Message) -> None:
    req = str(uuid.uuid4())
    set_request_id(req)
    logger.info(f"[TG] update start req={req} h=cmd_help")
    await message.answer(
        "Быстрые действия кнопками ниже.\n"
        "Команды для продвинутых: /show, /edit, /edititem, /comment, /save, /invoices.",
        reply_markup=main_kb(),
    )
    logger.info(f"[TG] update done req={req} h=cmd_help")

def setup(router: Router) -> None:
    router.message.register(cmd_start, F.text == "/start")
    router.message.register(cmd_help, F.text == "/help")
