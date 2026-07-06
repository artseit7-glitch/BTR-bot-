"""
Структурированное логирование для BTR Bot.
Все security-события пишутся как JSON — удобно фильтровать в Railway Logs.

Категории событий:
  CALC_OK       — успешный расчёт
  RATE_LIMITED  — пользователь заспамил (>1 req/sec)
  DAILY_LIMIT   — исчерпан дневной лимит расчётов
  INVALID_CB    — попытка отправить callback не из whitelist
  BOT_ERROR     — необработанное исключение
  STARTUP       — старт / остановка бота
"""

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any


def _make_logger() -> logging.Logger:
    logger = logging.getLogger("btr_bot")
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(_JsonFormatter())
    logger.addHandler(handler)
    logger.propagate = False
    return logger


class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts":    datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "event": getattr(record, "event", "LOG"),
            "msg":   record.getMessage(),
        }
        # Любые extra-поля (user_id, callback_data, …) прокидываются напрямую
        for key, val in record.__dict__.items():
            if key not in {
                "name", "msg", "args", "levelname", "levelno", "pathname",
                "filename", "module", "exc_info", "exc_text", "stack_info",
                "lineno", "funcName", "created", "msecs", "relativeCreated",
                "thread", "threadName", "processName", "process", "message",
                "event",
            }:
                payload[key] = val
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


log = _make_logger()


# ── Хелперы для конкретных событий ────────────────────────────────────────────

def calc_ok(user_id: int, username: str | None, floor_type: str, area: float) -> None:
    log.info("Calculation completed", extra={
        "event": "CALC_OK",
        "user_id": user_id,
        "username": username,
        "floor_type": floor_type,
        "area": area,
    })


def rate_limited(user_id: int, username: str | None) -> None:
    log.warning("Rate limit hit", extra={
        "event": "RATE_LIMITED",
        "user_id": user_id,
        "username": username,
    })


def daily_limit_hit(user_id: int, username: str | None, count: int) -> None:
    log.warning("Daily calc limit reached", extra={
        "event": "DAILY_LIMIT",
        "user_id": user_id,
        "username": username,
        "daily_count": count,
    })


def invalid_callback(user_id: int, username: str | None, cb_data: str) -> None:
    log.warning("Invalid callback data rejected", extra={
        "event": "INVALID_CB",
        "user_id": user_id,
        "username": username,
        "cb_data": cb_data,
    })


def bot_error(exc: Exception, context: str = "") -> None:
    log.error("Unhandled bot error", exc_info=exc, extra={
        "event": "BOT_ERROR",
        "context": context,
    })


def startup(mode: str = "polling") -> None:
    log.info("Bot started", extra={"event": "STARTUP", "mode": mode})


def shutdown() -> None:
    log.info("Bot stopped", extra={"event": "SHUTDOWN"})
