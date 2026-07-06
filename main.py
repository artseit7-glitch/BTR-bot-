import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ErrorEvent

import utils.logger as logger
from config import BOT_TOKEN, validate_env
from handlers import concrete, self_leveling, start, wooden
from middlewares.throttling import ThrottlingMiddleware


async def main():
    validate_env()
    logger.startup()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    throttle = ThrottlingMiddleware()
    dp.message.middleware(throttle)
    dp.callback_query.middleware(throttle)

    dp.include_router(start.router)
    dp.include_router(concrete.router)
    dp.include_router(self_leveling.router)
    dp.include_router(wooden.router)

    @dp.error()
    async def error_handler(event: ErrorEvent):
        logger.bot_error(event.exception)

    try:
        await dp.start_polling(bot)
    finally:
        logger.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
