import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from core.container import create_app_container
from handlers.callbacks import router as callbacks_router
from handlers.commands import router as cmd_router
from handlers.di_middleware import ContainerMiddleware
from handlers.file import router as file_router
from ocr.engine.util import get_logger

logger = get_logger("ocr.engine")
logger.info("Bot startup")


async def _run_bot() -> None:
    """
    Async entrypoint that initializes and runs the Telegram bot.
    """
    if BOT_TOKEN is None:
        raise ValueError("BOT_TOKEN is not set. Please check your config.py or environment variables.")
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    container = create_app_container()
    dp.update.outer_middleware(ContainerMiddleware(container))

    dp.include_router(file_router)
    dp.include_router(cmd_router)
    dp.include_router(callbacks_router)
    await dp.start_polling(bot)


def main() -> None:
    asyncio.run(_run_bot())


if __name__ == "__main__":
    main()
