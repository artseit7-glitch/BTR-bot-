import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WHATSAPP_LINK = "https://wa.me/message/GLBCF2WXYW5FD1"

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
