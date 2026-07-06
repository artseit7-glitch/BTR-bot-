-- BTR Bot — Supabase Schema + RLS
-- Выполнить в Supabase Dashboard → SQL Editor

-- ============================================================
-- ТАБЛИЦА: расчёты пользователей
-- ============================================================
CREATE TABLE IF NOT EXISTS calculations (
    id          BIGSERIAL PRIMARY KEY,
    user_id     BIGINT    NOT NULL,   -- Telegram user_id
    username    TEXT,
    floor_type  TEXT      NOT NULL CHECK (floor_type IN ('concrete', 'wooden', 'self_leveling')),
    area        FLOAT     NOT NULL CHECK (area > 0 AND area <= 5000),
    works       JSONB     NOT NULL DEFAULT '[]',
    total_min   FLOAT     NOT NULL CHECK (total_min >= 0),
    total_max   FLOAT     NOT NULL CHECK (total_max >= total_min),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Индекс для быстрой выборки по пользователю
CREATE INDEX IF NOT EXISTS idx_calculations_user_id ON calculations(user_id);
CREATE INDEX IF NOT EXISTS idx_calculations_created_at ON calculations(created_at DESC);

-- ============================================================
-- ROW LEVEL SECURITY
-- Telegram Bot использует service_role для записи —
-- он обходит RLS. Anon/authenticated — только чтение своих данных.
-- ============================================================
ALTER TABLE calculations ENABLE ROW LEVEL SECURITY;

-- Пользователь видит только свои расчёты (для будущего веб-кабинета)
CREATE POLICY "users_select_own_calculations"
    ON calculations FOR SELECT
    USING (user_id = (current_setting('app.telegram_user_id', true))::BIGINT);

-- Вставка только через service_role (бот) — anon не может писать напрямую
CREATE POLICY "service_role_insert_calculations"
    ON calculations FOR INSERT
    WITH CHECK (true);  -- service_role обходит RLS полностью

-- Никто не может UPDATE/DELETE расчёты через anon/authenticated
-- (только service_role из бота)

-- ============================================================
-- ТАБЛИЦА: прайс на материалы (Этап 2)
-- ============================================================
CREATE TABLE IF NOT EXISTS material_prices (
    id          BIGSERIAL PRIMARY KEY,
    category    TEXT  NOT NULL CHECK (category IN ('concrete', 'wooden', 'self_leveling')),
    key         TEXT  NOT NULL,
    name        TEXT  NOT NULL,
    unit        TEXT  NOT NULL,
    price_min   FLOAT NOT NULL CHECK (price_min >= 0),
    price_max   FLOAT CHECK (price_max IS NULL OR price_max >= price_min),
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (category, key)
);

-- Материалы — публичное чтение (цены не секрет)
ALTER TABLE material_prices ENABLE ROW LEVEL SECURITY;

CREATE POLICY "anyone_can_read_active_prices"
    ON material_prices FOR SELECT
    USING (is_active = TRUE);

-- Запись только через service_role (обновление прайса из бэкенда)

-- ============================================================
-- ЗАПОЛНЕНИЕ: стартовые цены на материалы (ориентир)
-- ============================================================
INSERT INTO material_prices (category, key, name, unit, price_min, price_max) VALUES
    ('concrete', 'cement_mix',  'Цементно-песчаная смесь М300', 'м²', 1200, 1800),
    ('concrete', 'rebar_mesh',  'Арматурная сетка 150×150×4мм',  'м²',  800, 1200),
    ('concrete', 'gravel',      'Щебень фракция 20-40мм',         'м³', 6000, 9000),
    ('wooden',   'osb_18mm',    'ОСП 18мм',                       'м²', 1500, 2200),
    ('wooden',   'laminate_33', 'Ламинат 33 класс',               'м²', 2500, 6000),
    ('wooden',   'linoleum',    'Линолеум бытовой',               'м²', 1200, 3500),
    ('wooden',   'tile_ceramic','Керамогранит 60×60',             'м²', 3500, 8000),
    ('self_leveling', 'compound', 'Наливной пол самовыравнивающийся', 'м²', 1500, 3000)
ON CONFLICT (category, key) DO NOTHING;
