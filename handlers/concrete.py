from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from calculators.concrete import calculate
from config import MAX_AREA, MAX_GRAVEL_DEPTH
from keyboards.main_kb import works_keyboard, consultation_keyboard
from utils.formatters import format_concrete

router = Router()


class ConcreteStates(StatesGroup):
    waiting_area = State()
    waiting_works = State()
    waiting_gravel_depth = State()


@router.callback_query(F.data == "floor:concrete")
async def start_concrete(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ConcreteStates.waiting_area)
    await callback.message.edit_text(
        "🧱 <b>Бетонные полы</b>\n\nВведите площадь помещения в м²:\n<i>например: 35.5</i>",
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(ConcreteStates.waiting_area)
async def get_concrete_area(message: Message, state: FSMContext):
    try:
        area = float(message.text.replace(",", "."))
        if not (0 < area <= MAX_AREA):
            raise ValueError
    except (ValueError, AttributeError):
        await message.answer(
            f"❌ Введите число от 1 до {MAX_AREA} (м²), например: <b>35.5</b>", parse_mode="HTML"
        )
        return

    await state.update_data(area=area, selected=[])
    await state.set_state(ConcreteStates.waiting_works)
    await message.answer(
        f"📐 Площадь: <b>{area} м²</b>\n\nВыберите виды работ и нажмите <b>Рассчитать</b>:",
        reply_markup=works_keyboard("concrete", set()),
        parse_mode="HTML",
    )


@router.callback_query(ConcreteStates.waiting_works, F.data.startswith("toggle:concrete:"))
async def toggle_concrete(callback: CallbackQuery, state: FSMContext):
    item = callback.data.split(":")[2]
    data = await state.get_data()
    selected = set(data.get("selected", []))
    selected.discard(item) if item in selected else selected.add(item)
    await state.update_data(selected=list(selected))
    await callback.message.edit_reply_markup(reply_markup=works_keyboard("concrete", selected))
    await callback.answer()


@router.callback_query(ConcreteStates.waiting_works, F.data == "calc:concrete")
async def calc_concrete(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected = set(data.get("selected", []))

    if not selected:
        await callback.answer("⚠️ Выберите хотя бы одну работу!", show_alert=True)
        return

    if "gravel" in selected:
        await state.set_state(ConcreteStates.waiting_gravel_depth)
        await callback.message.edit_text(
            "🪨 Введите глубину засыпки щебнем в <b>сантиметрах</b>:\n<i>от 10 до 100 см (10 см = 1 000 ₸/м², 100 см = 5 000 ₸/м²)</i>",
            parse_mode="HTML",
        )
        await callback.answer()
        return

    area = data["area"]
    result = calculate(area, list(selected))
    await callback.message.edit_text(
        format_concrete(area, result),
        reply_markup=consultation_keyboard(),
        parse_mode="HTML",
    )
    await state.clear()
    await callback.answer()


@router.message(ConcreteStates.waiting_gravel_depth)
async def get_gravel_depth(message: Message, state: FSMContext):
    try:
        depth = int(message.text.strip())
        if not (1 <= depth <= MAX_GRAVEL_DEPTH):
            raise ValueError
    except (ValueError, AttributeError):
        await message.answer(f"❌ Введите целое число от 1 до {MAX_GRAVEL_DEPTH} (в сантиметрах).")
        return

    data = await state.get_data()
    result = calculate(data["area"], data["selected"], gravel_depth=depth)
    await message.answer(
        format_concrete(data["area"], result),
        reply_markup=consultation_keyboard(),
        parse_mode="HTML",
    )
    await state.clear()
