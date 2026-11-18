import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from backend.config import BOT_TOKEN
from backend.core.container import create_app_container
from backend.handlers.callbacks import router as callbacks_router
from backend.handlers.commands import router as cmd_router
from backend.handlers.di_middleware import ContainerMiddleware
from backend.handlers.file import router as file_router
from backend.handlers.language import register_bot_commands
from backend.handlers.locale_middleware import LocaleMiddleware
from backend.ocr.engine.util import get_logger
from backend.storage.db import DB_PATH, init_db
from backend.storage.user_languages import UserLanguageStorage

logger = get_logger("ocr.engine")
logger.info("Bot startup")


async def _run_bot() -> None:
    if BOT_TOKEN is None:
        raise ValueError(
            "BOT_TOKEN is not set. Please check your config.py or environment variables."
        )
    init_db()
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    await register_bot_commands(bot)

    container = create_app_container()
    dp.update.outer_middleware(ContainerMiddleware(container))
    dp.update.outer_middleware(LocaleMiddleware(UserLanguageStorage(DB_PATH)))

    dp.include_router(file_router)
    dp.include_router(cmd_router)
    dp.include_router(callbacks_router)
    await dp.start_polling(bot)


def main() -> None:
    asyncio.run(_run_bot())


if __name__ == "__main__":
    main()
