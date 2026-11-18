import asyncio
import logging
from weakref import WeakValueDictionary

from aiogram import Bot, F, Router
from aiogram.enums import ChatType
from aiogram.exceptions import TelegramAPIError
from aiogram.types import BotCommand, BotCommandScopeChat, CallbackQuery, Message

from backend.handlers import texts
from backend.handlers.callback_registry import LANGUAGE_PREFIX, CallbackAction
from backend.handlers.utils import language_kb, main_kb
from backend.storage.user_languages import UserLanguageStorage

logger = logging.getLogger(__name__)
_selection_locks: WeakValueDictionary[int, asyncio.Lock] = WeakValueDictionary()

_COMMANDS = {
    "start": "CMD_DESC_START",
    "help": "CMD_DESC_HELP",
    "show": "CMD_DESC_SHOW",
    "save": "CMD_DESC_SAVE",
    "invoices": "CMD_DESC_INVOICES",
    "language": "CMD_DESC_LANGUAGE",
}


def bot_commands(locale: str) -> list[BotCommand]:
    return [
        BotCommand(command=command, description=texts.t(key, locale=locale))
        for command, key in _COMMANDS.items()
    ]


async def register_bot_commands(bot: Bot) -> None:
    await bot.set_my_commands(bot_commands(texts.DEFAULT_LOCALE))
    for locale in texts.LANGUAGES:
        await bot.set_my_commands(bot_commands(locale), language_code=locale)


async def show_languages(call: CallbackQuery) -> None:
    await call.answer()
    if isinstance(call.message, Message):
        await call.message.answer(texts.t("LANGUAGE_PROMPT"), reply_markup=language_kb())


async def change_language(
    call: CallbackQuery,
    bot: Bot,
    language_storage: UserLanguageStorage,
) -> None:
    locale = (call.data or "").removeprefix(LANGUAGE_PREFIX)
    message = call.message
    if locale not in texts.LANGUAGES or not isinstance(message, Message):
        await call.answer()
        return

    user_id = call.from_user.id
    # Keep each user's saved preference and Telegram command menu in the same order.
    lock = _selection_locks.setdefault(user_id, asyncio.Lock())
    async with lock:
        await language_storage.set(user_id, locale)
        await call.answer()
        if message.chat.type == ChatType.PRIVATE:
            try:
                await bot.set_my_commands(
                    bot_commands(locale), scope=BotCommandScopeChat(chat_id=message.chat.id)
                )
            except TelegramAPIError:
                logger.warning("Could not update the private command menu", exc_info=True)
        with texts.use_locale(locale):
            await message.answer(texts.t("LANGUAGE_CHANGED"), reply_markup=main_kb())


def setup(router: Router) -> None:
    router.callback_query.register(show_languages, F.data == CallbackAction.LANGUAGE.value)
    router.callback_query.register(change_language, F.data.startswith(LANGUAGE_PREFIX))
