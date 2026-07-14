from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import WHATSAPP_LINK

CONCRETE_WORKS = {
    "screed":     "Заливка стяжки",
    "beacons":    "Выставление маяков",
    "gravel":     "Засыпка щебнем",
    "rebar":      "Вязка арматуры",
    "demolition": "Демонтаж",
}

WOODEN_WORKS = {
    "lags":     "Установка лаг",
    "osb":      "Укладка ОСП/фанеры",
    "laminate": "Укладка ламината",
    "linoleum": "Настил линолеума",
    "tile":     "Укладка плитки",
    "plinth":   "Монтаж плинтуса",
}


def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧱 Бетонные полы",   callback_data="floor:concrete")],
        [InlineKeyboardButton(text="💧 Наливные полы",   callback_data="floor:self_leveling")],
        [InlineKeyboardButton(text="🪵 Деревянные полы", callback_data="floor:wooden")],
        [InlineKeyboardButton(text="🤖 AI Ассистент",    callback_data="ai_assistant")],
    ])


def works_keyboard(floor_type: str, selected: set) -> InlineKeyboardMarkup:
    works = CONCRETE_WORKS if floor_type == "concrete" else WOODEN_WORKS
    buttons = []
    for key, label in works.items():
        mark = "✅" if key in selected else "☐"
        buttons.append([InlineKeyboardButton(
            text=f"{mark} {label}",
            callback_data=f"toggle:{floor_type}:{key}",
        )])
    buttons.append([InlineKeyboardButton(text="📊 Рассчитать", callback_data=f"calc:{floor_type}")])
    buttons.append([InlineKeyboardButton(text="🔙 Главное меню", callback_data="menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def consultation_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📲 Бесплатная консультация", url=WHATSAPP_LINK)],
        [InlineKeyboardButton(text="🔙 Главное меню", callback_data="menu")],
    ])


def ai_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Новый диалог",            callback_data="ai_reset")],
        [InlineKeyboardButton(text="📲 Бесплатная консультация", url=WHATSAPP_LINK)],
        [InlineKeyboardButton(text="🔙 Главное меню",            callback_data="menu")],
    ])
