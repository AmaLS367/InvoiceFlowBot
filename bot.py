import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers.file import router as file_router
from handlers.commands import router as cmd_router
from ocr.engine.util import get_logger

logger = get_logger("ocr.engine")
logger.info("Bot startup")

async def main():
    if BOT_TOKEN is None:
        raise ValueError("BOT_TOKEN is not set. Please check your config.py or environment variables.")
    bot = Bot(token=BOT_TOKEN)  
    dp = Dispatcher()
    dp.include_router(file_router)
    dp.include_router(cmd_router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
