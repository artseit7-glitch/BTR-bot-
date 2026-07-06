from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from calculators.self_leveling import calculate
from config import MAX_AREA
from keyboards.main_kb import consultation_keyboard
from utils.formatters import format_self_leveling

router = Router()


class SelfLevelingStates(StatesGroup):
    waiting_area = State()


@router.callback_query(F.data == "floor:self_leveling")
async def start_self_leveling(callback: CallbackQuery, state: FSMContext):
    await state.set_state(SelfLevelingStates.waiting_area)
    await callback.message.edit_text(
        "💧 <b>Наливные полы</b>\n\nВведите площадь помещения в м²:\n<i>например: 35.5</i>",
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(SelfLevelingStates.waiting_area)
async def get_area(message: Message, state: FSMContext):
    try:
        area = float(message.text.replace(",", "."))
        if not (0 < area <= MAX_AREA):
            raise ValueError
    except (ValueError, AttributeError):
        await message.answer(
            f"❌ Введите число от 1 до {MAX_AREA} (м²), например: <b>35.5</b>", parse_mode="HTML"
        )
        return

    total = calculate(area)["self_leveling"]
    await message.answer(
        format_self_leveling(area, total),
        reply_markup=consultation_keyboard(),
        parse_mode="HTML",
    )
    await state.clear()
