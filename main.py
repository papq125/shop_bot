import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
import os

from database.db import init_db
from handlers.start import router as start_router
from handlers.catalog import router as catalog_router
from handlers.cart import router as cart_router
from handlers.checkout import router as checkout_router
from handlers.admin import router as admin_router
from handlers.promo import router as promo_router

load_dotenv()
logging.basicConfig(level=logging.INFO)

async def main():
    await init_db()
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start_router)
    dp.include_router(catalog_router)
    dp.include_router(cart_router)
    dp.include_router(checkout_router)
    dp.include_router(promo_router)
    dp.include_router(admin_router)

    print("✅ Бот запущений!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
