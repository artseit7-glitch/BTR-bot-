import time
from collections import defaultdict
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


class ThrottlingMiddleware(BaseMiddleware):
    """Max 1 request per RATE_LIMIT seconds per user. Excess requests are silently dropped."""

    RATE_LIMIT = 1.0  # seconds between allowed requests

    def __init__(self):
        self._last_seen: Dict[int, float] = defaultdict(float)

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if user:
            now = time.monotonic()
            if now - self._last_seen[user.id] < self.RATE_LIMIT:
                return
            self._last_seen[user.id] = now
        return await handler(event, data)
