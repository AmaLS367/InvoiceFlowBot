"""
Common command handlers: /start, /help, etc.
"""

import uuid

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from backend.handlers import texts
from backend.handlers.utils import language_kb, main_kb
from backend.ocr.engine.util import get_logger, set_request_id

logger = get_logger("ocr.engine")


async def cmd_start(message: Message, preferred_language: str | None = None) -> None:
    req = str(uuid.uuid4())
    set_request_id(req)
    logger.info(f"[TG] update start req={req} h=cmd_start")
    if preferred_language in texts.LANGUAGES:
        await message.answer(texts.t("START_TEXT"), reply_markup=main_kb())
    else:
        await cmd_language(message)
    logger.info(f"[TG] update done req={req} h=cmd_start")


async def cmd_help(message: Message) -> None:
    req = str(uuid.uuid4())
    set_request_id(req)
    logger.info(f"[TG] update start req={req} h=cmd_help")
    await message.answer(
        texts.t("HELP_TEXT"),
        reply_markup=main_kb(),
    )
    logger.info(f"[TG] update done req={req} h=cmd_help")


async def cmd_language(message: Message) -> None:
    await message.answer(texts.t("LANGUAGE_PROMPT"), reply_markup=language_kb())


def setup(router: Router) -> None:
    router.message.register(cmd_start, CommandStart())
    router.message.register(cmd_help, F.text == "/help")
    router.message.register(cmd_language, Command("language"))
