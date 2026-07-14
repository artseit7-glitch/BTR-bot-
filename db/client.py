import os
from supabase import create_client, Client

_client: Client | None = None


def get_client() -> Client:
    """Возвращает singleton Supabase client с service_role ключом.
    service_role используется только server-side (в боте), никогда не передаётся клиенту.
    """
    global _client
    if _client is None:
        url = os.environ["SUPABASE_URL"]
        key = os.environ["SUPABASE_SERVICE_KEY"]  # читаем напрямую, не из config-модуля
        _client = create_client(url, key)
    return _client


async def log_calculation(
    user_id: int,
    username: str | None,
    floor_type: str,
    area: float,
    works: list,
    total_min: float,
    total_max: float,
) -> None:
    """Сохраняет расчёт. user_id берётся из Telegram-объекта, не из запроса пользователя."""
    client = get_client()
    client.table("calculations").insert({
        "user_id":    user_id,
        "username":   username,
        "floor_type": floor_type,
        "area":       area,
        "works":      works,
        "total_min":  total_min,
        "total_max":  total_max,
    }).execute()


async def get_material_prices(category: str) -> list[dict]:
    """Возвращает активные цены на материалы для категории."""
    client = get_client()
    result = (
        client.table("material_prices")
        .select("key, name, unit, price_min, price_max")
        .eq("category", category)
        .eq("is_active", True)
        .execute()
    )
    return result.data


def load_conversation(user_id: int) -> list[dict]:
    """Загружает историю диалога пользователя из Supabase."""
    client = get_client()
    result = (
        client.table("conversations")
        .select("messages")
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    if result.data:
        return result.data[0]["messages"]
    return []


def save_conversation(user_id: int, messages: list[dict]) -> None:
    """Сохраняет историю диалога (upsert по user_id)."""
    client = get_client()
    client.table("conversations").upsert(
        {"user_id": user_id, "messages": messages},
        on_conflict="user_id",
    ).execute()


def clear_conversation(user_id: int) -> None:
    """Сбрасывает историю диалога пользователя."""
    client = get_client()
    client.table("conversations").delete().eq("user_id", user_id).execute()
