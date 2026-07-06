import time
from collections import defaultdict
from datetime import date
from typing import Any, Awaitable, Callable, Dict, Tuple

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, TelegramObject

import utils.logger as logger

DAILY_CALC_LIMIT = 50
CALC_CALLBACKS = frozenset({"calc:concrete", "calc:wooden"})


class ThrottlingMiddleware(BaseMiddleware):
    RATE_LIMIT = 1.0

    def __init__(self):
        self._last_seen: Dict[int, float] = defaultdict(float)
        self._daily_counts: Dict[Tuple[int, date], int] = defaultdict(int)

    def _check_daily(self, user_id: int) -> bool:
        return self._daily_counts[(user_id, date.today())] < DAILY_CALC_LIMIT

    def _increment_daily(self, user_id: int) -> int:
        key = (user_id, date.today())
        self._daily_counts[key] += 1
        if self._daily_counts[key] % 20 == 0:
            today = date.today()
            for k in list(self._daily_counts):
                if k[1] < today:
                    del self._daily_counts[k]
        return self._daily_counts[key]

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if not user:
            return await handler(event, data)

        # Уровень 1: per-second throttle
        now = time.monotonic()
        if now - self._last_seen[user.id] < self.RATE_LIMIT:
            logger.rate_limited(user.id, user.username)
            return
        self._last_seen[user.id] = now

        # Уровень 2: daily calc limit
        if isinstance(event, CallbackQuery) and event.data in CALC_CALLBACKS:
            if not self._check_daily(user.id):
                count = self._daily_counts[(user.id, date.today())]
                logger.daily_limit_hit(user.id, user.username, count)
                await event.answer(
                    f"⛔ Лимит {DAILY_CALC_LIMIT} расчётов в сутки исчерпан.\n"
                    "Нажмите 📲 для консультации — мы поможем вручную!",
                    show_alert=True,
                )
                return
            self._increment_daily(user.id)

        return await handler(event, data)
