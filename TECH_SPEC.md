# TECH SPEC — BTR Bot

## Инфраструктура

| Слой | Сервис | Назначение |
|---|---|---|
| Runtime | Python 3.11+ | Язык разработки |
| Bot framework | aiogram 3.x | Async Telegram Bot |
| Хостинг | Railway | Деплой и запуск бота |
| VCS / CI-CD | GitHub → Railway | Push в main → авто-деплой |
| База данных | Supabase (PostgreSQL) | Аналитика, история, материалы (этап 2+) |
| FSM-хранилище | MemoryStorage | Этап 1 (in-process, сбрасывается при рестарте) |

---

## Deployment Flow

```
Локальная разработка
        │
        ▼
  git push → GitHub (main)
        │
        ▼  (webhook / GitHub Actions)
     Railway
        │
        ▼
  python main.py  (polling mode)
```

Railway автоматически:
- Определяет Python-проект через `requirements.txt` (nixpacks)
- Собирает образ
- Запускает `python main.py`
- Перезапускает бот при каждом пуше в `main`

---

## Environment Variables

Устанавливаются в **Railway Dashboard → Variables**:

| Переменная | Описание | Источник |
|---|---|---|
| `BOT_TOKEN` | Токен Telegram-бота | @BotFather |
| `SUPABASE_URL` | URL проекта Supabase | Dashboard Supabase |
| `SUPABASE_ANON_KEY` | Публичный ключ Supabase | Dashboard → API |
| `SUPABASE_SERVICE_KEY` | Сервисный ключ (полный доступ) | Dashboard → API |

---

## Supabase — схема БД

### Этап 1 (опционально — аналитика)
```sql
-- Лог расчётов
CREATE TABLE calculations (
    id          BIGSERIAL PRIMARY KEY,
    user_id     BIGINT    NOT NULL,
    username    TEXT,
    floor_type  TEXT      NOT NULL,  -- 'concrete' | 'wooden' | 'self_leveling'
    area        FLOAT,
    works       JSONB,               -- выбранные виды работ
    total_min   FLOAT,
    total_max   FLOAT,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);
```

### Этап 2 (расчёт с материалами)
```sql
-- Прайс на материалы (редактируется без деплоя)
CREATE TABLE material_prices (
    id          BIGSERIAL PRIMARY KEY,
    category    TEXT NOT NULL,   -- 'concrete' | 'wooden' | 'self_leveling'
    name        TEXT NOT NULL,
    unit        TEXT NOT NULL,   -- 'м²' | 'м³' | 'шт' | 'п.м.'
    price_min   FLOAT NOT NULL,
    price_max   FLOAT,
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);
```

### Этап 3 (AI-ассистент)
```sql
-- История диалогов
CREATE TABLE conversations (
    id          BIGSERIAL PRIMARY KEY,
    user_id     BIGINT NOT NULL,
    messages    JSONB NOT NULL,  -- [{role, content}]
    created_at  TIMESTAMPTZ DEFAULT NOW()
);
```

---

## Структура репозитория

```
BTR-bot-/          ← GitHub repo: artseit7-glitch/BTR-bot-
├── main.py
├── config.py
├── requirements.txt
├── Procfile           ← Railway: "worker: python main.py"
├── .env.example
├── .gitignore
├── handlers/
├── keyboards/
├── calculators/
└── utils/
```

---

## Зависимости (requirements.txt)

| Пакет | Этап | Назначение |
|---|---|---|
| `aiogram==3.7.0` | 1 | Telegram Bot framework |
| `python-dotenv==1.0.1` | 1 | Загрузка `.env` |
| `supabase==2.x` | 2 | Клиент Supabase |

---

## Безопасность

- `.env` в `.gitignore` — токены не попадают в репозиторий
- Все секреты хранятся в Railway Environment Variables
- `SUPABASE_SERVICE_KEY` используется только в серверном коде, никогда на клиенте
- `SUPABASE_ANON_KEY` имеет ограниченные RLS-права (Row Level Security)

---

## Масштабирование

- **Этап 1**: MemoryStorage — достаточно. Один инстанс на Railway.
- **Этап 2**: Если нужен Redis FSM (несколько инстансов) → `aiogram-contrib` + Redis add-on Railway.
- **Этап 3**: AI-вызовы через отдельный микросервис или напрямую в хендлере с timeout.

---

## GitHub Repository
- URL: https://github.com/artseit7-glitch/BTR-bot-
- Branch: `main`
- Auto-deploy: Railway подключён к `main`

## Supabase Project
- URL: см. `SUPABASE_URL` в Railway Variables
- Project ref: см. `SUPABASE_URL` в Railway Variables
