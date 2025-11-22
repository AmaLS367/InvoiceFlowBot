import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from handlers.callbacks import router as callbacks_router
from handlers.commands import router as cmd_router
from handlers.file import router as file_router
from ocr.engine.util import get_logger

logger = get_logger("ocr.engine")
logger.info("Bot startup")

async def main():
    if BOT_TOKEN is None:
        raise ValueError("BOT_TOKEN is not set. Please check your config.py or environment variables.")
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(file_router)
    dp.include_router(cmd_router)
    dp.include_router(callbacks_router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
