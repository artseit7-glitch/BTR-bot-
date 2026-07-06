import os
import sys
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WHATSAPP_LINK = "https://wa.me/message/GLBCF2WXYW5FD1"

# Supabase — загружаем только когда реально нужно (Этап 2+)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
# SERVICE_KEY не экспортируем в модуль — читается напрямую через os.getenv в db-слое

# Лимиты пользовательского ввода
MAX_AREA = 5_000       # м² — разумный максимум для жилого/коммерческого объекта
MAX_GRAVEL_DEPTH = 100  # см
MAX_PLINTH_METERS = 2_000  # п.м.


def validate_env() -> None:
    """Проверяем обязательные переменные при старте. Падаем явно, не в середине запроса."""
    if not BOT_TOKEN:
        print("FATAL: BOT_TOKEN is not set. Add it to Railway Variables.", file=sys.stderr)
        sys.exit(1)


# Бетонные полы (₸/м²)
CONCRETE = {
    "screed": 5000,
    "beacons": 1000,
    "gravel_per_cm": 50,  # 50₸/см/м², мин 1000₸: 10см=1000₸, 100см=5000₸
    "gravel_min": 1000,
    "rebar": 1200,
    "demolition": 1000,
}

# Наливные полы (₸/м²)
SELF_LEVELING = {
    "min": 4000,
}

# Деревянные полы (₸/м² или ₸/п.м. для плинтуса) — (min, max)
WOODEN = {
    "lags":     (1500, 2500),
    "osb":      (2000, 3000),
    "laminate": (1500, 2500),
    "linoleum": (800,  1500),
    "tile":     (5000, 10000),
    "plinth":   (600,  1200),
}
