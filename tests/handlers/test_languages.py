import json
from datetime import UTC, datetime
from importlib.resources import files
from string import Formatter
from unittest.mock import AsyncMock

import pytest
from aiogram import Bot, Dispatcher, Router
from aiogram.methods import SendMessage, SetMyCommands
from aiogram.types import CallbackQuery, Chat, InlineKeyboardMarkup, Message, Update, User

from backend.handlers import texts
from backend.handlers.callbacks_misc import setup as setup_misc_callbacks
from backend.handlers.commands_common import setup as setup_commands
from backend.handlers.language import register_bot_commands
from backend.handlers.language import setup as setup_language_callbacks
from backend.handlers.locale_middleware import LocaleMiddleware
from backend.storage.user_languages import UserLanguageStorage


def _dispatcher(storage: UserLanguageStorage) -> Dispatcher:
    dispatcher = Dispatcher()
    dispatcher.update.outer_middleware(LocaleMiddleware(storage))
    router = Router()
    setup_commands(router)
    setup_misc_callbacks(router)
    setup_language_callbacks(router)
    dispatcher.include_router(router)
    return dispatcher


def _message(user: User, text: str | None = None) -> Message:
    return Message(
        message_id=1,
        date=datetime.now(UTC),
        chat=Chat(id=user.id, type="private"),
        from_user=user,
        text=text,
    )


def _callback(user: User, data: str) -> Update:
    message = _message(user).model_copy(
        update={"from_user": User(id=999, is_bot=True, first_name="Bot")}
    )
    return Update(
        update_id=1,
        callback_query=CallbackQuery(
            id="test", from_user=user, chat_instance="test", message=message, data=data
        ),
    )


def _buttons(message: SendMessage) -> dict[str | None, str]:
    assert isinstance(message.reply_markup, InlineKeyboardMarkup)
    return {
        button.callback_data: button.text
        for row in message.reply_markup.inline_keyboard
        for button in row
    }


@pytest.mark.asyncio
async def test_registers_localized_telegram_command_menus() -> None:
    bot = Bot("123:fake", session=AsyncMock())
    await register_bot_commands(bot)

    menus = {call.args[1].language_code: call.args[1] for call in bot.session.call_args_list}
    assert set(menus) == {None, "ru", "en"}
    assert menus["en"].commands[-1].command == "language"
    assert menus["en"].commands[-1].description == "Choose a language"
    assert menus["ru"].commands[-1].description == "Выбрать язык"
    assert menus[None].commands == menus["ru"].commands


@pytest.mark.asyncio
async def test_start_and_menu_change_language_and_keep_it_after_restart(
    test_db_path, migrated_database_url
) -> None:
    bot = Bot("123:fake", session=AsyncMock())
    dispatcher = _dispatcher(UserLanguageStorage(str(test_db_path)))
    user = User(id=42, is_bot=False, first_name="User", language_code="en-US")

    async def dispatch(update: Update) -> tuple[SendMessage, list[SetMyCommands]]:
        bot.session.reset_mock()
        await dispatcher.feed_update(bot, update)
        methods = [call.args[1] for call in bot.session.call_args_list]
        [message] = [method for method in methods if isinstance(method, SendMessage)]
        return message, [method for method in methods if isinstance(method, SetMyCommands)]

    async def command(text: str, sender: User = user) -> SendMessage:
        message, _ = await dispatch(Update(update_id=1, message=_message(sender, text)))
        return message

    welcome = await command("/start")
    assert "Choose your language." in welcome.text
    assert _buttons(welcome)["language:ru"] == "Русский"
    assert _buttons(welcome)["language:en"] == "English"

    confirmation, [menu] = await dispatch(_callback(user, "language:ru"))
    assert confirmation.text == "Язык интерфейса изменён."
    assert menu.scope.chat_id == user.id
    assert menu.commands[-1].description == "Выбрать язык"
    assert _buttons(confirmation)["act_language"] == "🌐 Язык"

    dispatcher = _dispatcher(UserLanguageStorage(str(test_db_path)))
    picker = await command("/language")
    assert picker.text == "Выберите язык интерфейса."
    assert _buttons(picker) == {"language:ru": "Русский", "language:en": "English"}

    inline_picker, _ = await dispatch(_callback(user, "act_language"))
    assert inline_picker.text == picker.text
    assert _buttons(inline_picker) == _buttons(picker)

    confirmation, [menu] = await dispatch(_callback(user, "language:en"))
    assert confirmation.text == "Language updated."
    assert menu.commands[-1].description == "Choose a language"
    assert _buttons(confirmation)["act_language"] == "🌐 Language"

    upload, _ = await dispatch(_callback(user, "act_upload"))
    assert upload.text.startswith("Send a PDF or a photo")

    other_user = User(id=43, is_bot=False, first_name="Other", language_code="fr")
    assert (await command("/language", other_user)).text == "Выберите язык интерфейса."


def test_catalogs_use_the_same_keys_and_placeholders() -> None:
    def placeholders(locale: str) -> dict[str, set[str]]:
        catalog = json.loads(
            files("backend.handlers").joinpath("locales", f"{locale}.json").read_text("utf-8")
        )
        return {
            key: {field for _, field, _, _ in Formatter().parse(template) if field is not None}
            for key, template in catalog.items()
        }

    expected = placeholders(texts.DEFAULT_LOCALE)
    for locale in texts.LANGUAGES:
        assert placeholders(locale) == expected
