import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from handlers import concrete, self_leveling, start, wooden


async def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start.router)
    dp.include_router(concrete.router)
    dp.include_router(self_leveling.router)
    dp.include_router(wooden.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
