"""
Webhook-режим с проверкой подписи Telegram.

Сейчас бот работает в polling-режиме — этот файл не используется.
Для перехода на webhook (нужен публичный HTTPS-домен):

1. Установить: pip install aiohttp
2. Установить SECRET_TOKEN в Railway Variables
3. Зарегистрировать webhook:
   await bot.set_webhook(
       url="https://your-domain.com/webhook",
       secret_token=WEBHOOK_SECRET,
   )
4. Заменить dp.start_polling(bot) в main.py на start_webhook() ниже.

Telegram подписывает каждый запрос заголовком X-Telegram-Bot-Api-Secret-Token.
Без совпадения токена — запрос отклоняется с 403.
"""

import os
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET_TOKEN", "")
WEBHOOK_PATH = "/webhook"


async def start_webhook(bot: Bot, dp: Dispatcher) -> None:
    if not WEBHOOK_SECRET:
        logging.warning(
            "WEBHOOK_SECRET_TOKEN is not set — webhook requests will not be verified!"
        )

    app = web.Application()

    handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=WEBHOOK_SECRET,  # Telegram проверяет X-Telegram-Bot-Api-Secret-Token
    )
    handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    await web.run_app(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8080)),
    )
