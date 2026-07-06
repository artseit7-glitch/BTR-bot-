import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ErrorEvent

from config import BOT_TOKEN, validate_env
from handlers import concrete, self_leveling, start, wooden
from middlewares.throttling import ThrottlingMiddleware


async def main():
    validate_env()  # явно падаем если BOT_TOKEN не задан

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Rate limiting: 1 запрос/сек на пользователя
    dp.message.middleware(ThrottlingMiddleware())
    dp.callback_query.middleware(ThrottlingMiddleware())

    dp.include_router(start.router)
    dp.include_router(concrete.router)
    dp.include_router(self_leveling.router)
    dp.include_router(wooden.router)

    @dp.error()
    async def error_handler(event: ErrorEvent):
        logging.exception("Unhandled error: %s", event.exception)
        # не пробрасываем детали ошибки пользователю

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
