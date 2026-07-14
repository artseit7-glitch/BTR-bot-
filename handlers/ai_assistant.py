import asyncio
import os

import openai
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from keyboards.main_kb import ai_keyboard, main_menu

router = Router()

MAX_HISTORY = 20  # последние 20 сообщений (10 диалоговых пар)

SYSTEM_PROMPT = """Ты — AI-ассистент компании BTR (Казахстан). Компания специализируется на профессиональной укладке полов.

Помогай клиентам:
• Консультируй по видам работ и технологиям укладки полов
• Объясняй разницу между типами полов (бетонная стяжка, наливные, деревянные)
• Рекомендуй подходящий тип пола под задачу клиента
• Отвечай на вопросы о процессе и сроках работ

Актуальные цены на работы (без учёта материалов):

Бетонные полы:
— Заливка стяжки: 5 000 ₸/м²
— Выставление маяков: 1 000 ₸/м²
— Засыпка щебнем: от 1 000 ₸/м² (10 см) до 5 000 ₸/м² (100 см)
— Вязка арматуры: 1 200 ₸/м²
— Демонтаж: от 1 000 ₸/м²

Наливные полы:
— Наливной пол: от 4 000 ₸/м²

Деревянные полы:
— Установка лаг: 1 500–2 500 ₸/м²
— Укладка ОСП/фанеры: 2 000–3 000 ₸/м²
— Укладка ламината: 1 500–2 500 ₸/м²
— Настил линолеума: 800–1 500 ₸/м²
— Укладка плитки/керамогранита: 5 000–10 000 ₸/м²
— Монтаж плинтуса: 600–1 200 ₸/п.м.

Правила:
• Отвечай только на русском языке
• Будь вежливым, профессиональным и кратким
• Цены указаны только за работу, без материалов
• Если нужен точный расчёт — предложи воспользоваться калькулятором в главном меню
• Если клиент хочет вызвать мастера — упомяни бесплатную WhatsApp консультацию
• Не давай точных гарантий по срокам — только ориентировочные
• Не отвечай на вопросы, не связанные с укладкой полов"""


class AIDialog(StatesGroup):
    active = State()


def _get_ai_client() -> openai.AsyncOpenAI:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY не установлен")
    return openai.AsyncOpenAI(api_key=api_key)


def _load_history(user_id: int) -> list[dict]:
    try:
        from db.client import load_conversation
        return load_conversation(user_id)
    except Exception:
        return []


def _save_history(user_id: int, messages: list[dict]) -> None:
    try:
        from db.client import save_conversation
        save_conversation(user_id, messages)
    except Exception:
        pass


def _clear_history(user_id: int) -> None:
    try:
        from db.client import clear_conversation
        clear_conversation(user_id)
    except Exception:
        pass


@router.callback_query(F.data == "ai_assistant")
async def start_ai(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(AIDialog.active)
    await callback.message.answer(
        "🤖 <b>AI Ассистент BTR</b>\n\n"
        "Задайте любой вопрос о полах — виды работ, цены, что лучше выбрать.\n\n"
        "<i>История диалога сохраняется между сессиями.</i>",
        parse_mode="HTML",
        reply_markup=ai_keyboard(),
    )
    await callback.answer()


@router.callback_query(AIDialog.active, F.data == "ai_reset")
async def reset_ai(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    await asyncio.to_thread(_clear_history, user_id)
    await callback.message.answer(
        "🔄 Диалог сброшен. Начинаем новый разговор!\n\nЗадайте ваш вопрос:",
        reply_markup=ai_keyboard(),
    )
    await callback.answer()


@router.message(AIDialog.active, F.text)
async def handle_user_message(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_text = message.text

    history: list[dict] = await asyncio.to_thread(_load_history, user_id)

    history.append({"role": "user", "content": user_text})
    if len(history) > MAX_HISTORY:
        history = history[-MAX_HISTORY:]

    thinking_msg = await message.answer("🤔 Думаю...")

    try:
        ai = _get_ai_client()
        response = await ai.chat.completions.create(
            model="gpt-4o",
            max_tokens=1024,
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, *history],
        )
        reply_text = response.choices[0].message.content
    except RuntimeError as e:
        await thinking_msg.edit_text(f"⚠️ {e}")
        return
    except Exception:
        await thinking_msg.edit_text(
            "❌ Ошибка при обращении к AI. Попробуйте чуть позже."
        )
        return

    history.append({"role": "assistant", "content": reply_text})
    await asyncio.to_thread(_save_history, user_id, history)

    await thinking_msg.edit_text(reply_text, reply_markup=ai_keyboard())


@router.message(AIDialog.active)
async def handle_non_text(message: Message):
    await message.answer("Пожалуйста, отправьте текстовый вопрос.")
