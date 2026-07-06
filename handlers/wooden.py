from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from calculators.wooden import calculate
from keyboards.main_kb import works_keyboard, consultation_keyboard
from utils.formatters import format_wooden

router = Router()


class WoodenStates(StatesGroup):
    waiting_area = State()
    waiting_works = State()
    waiting_plinth_meters = State()


@router.callback_query(F.data == "floor:wooden")
async def start_wooden(callback: CallbackQuery, state: FSMContext):
    await state.set_state(WoodenStates.waiting_area)
    await callback.message.edit_text(
        "🪵 <b>Деревянные полы</b>\n\nВведите площадь помещения в м²:\n<i>например: 35.5</i>",
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(WoodenStates.waiting_area)
async def get_wooden_area(message: Message, state: FSMContext):
    try:
        area = float(message.text.replace(",", "."))
        if area <= 0:
            raise ValueError
    except (ValueError, AttributeError):
        await message.answer("❌ Введите корректное число, например: <b>35.5</b>", parse_mode="HTML")
        return

    await state.update_data(area=area, selected=[])
    await state.set_state(WoodenStates.waiting_works)
    await message.answer(
        f"📐 Площадь: <b>{area} м²</b>\n\nВыберите виды работ и нажмите <b>Рассчитать</b>:",
        reply_markup=works_keyboard("wooden", set()),
        parse_mode="HTML",
    )


@router.callback_query(WoodenStates.waiting_works, F.data.startswith("toggle:wooden:"))
async def toggle_wooden(callback: CallbackQuery, state: FSMContext):
    item = callback.data.split(":")[2]
    data = await state.get_data()
    selected = set(data.get("selected", []))
    selected.discard(item) if item in selected else selected.add(item)
    await state.update_data(selected=list(selected))
    await callback.message.edit_reply_markup(reply_markup=works_keyboard("wooden", selected))
    await callback.answer()


@router.callback_query(WoodenStates.waiting_works, F.data == "calc:wooden")
async def calc_wooden(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected = set(data.get("selected", []))

    if not selected:
        await callback.answer("⚠️ Выберите хотя бы одну работу!", show_alert=True)
        return

    if "plinth" in selected:
        await state.set_state(WoodenStates.waiting_plinth_meters)
        await callback.message.edit_text(
            "📏 Введите количество <b>погонных метров</b> плинтуса:\n<i>например: 24</i>",
            parse_mode="HTML",
        )
        await callback.answer()
        return

    area = data["area"]
    result = calculate(area, list(selected))
    await callback.message.edit_text(
        format_wooden(area, result),
        reply_markup=consultation_keyboard(),
        parse_mode="HTML",
    )
    await state.clear()
    await callback.answer()


@router.message(WoodenStates.waiting_plinth_meters)
async def get_plinth_meters(message: Message, state: FSMContext):
    try:
        meters = float(message.text.replace(",", "."))
        if meters <= 0:
            raise ValueError
    except (ValueError, AttributeError):
        await message.answer("❌ Введите корректное число, например: <b>24</b>", parse_mode="HTML")
        return

    data = await state.get_data()
    result = calculate(data["area"], data["selected"], plinth_meters=meters)
    await message.answer(
        format_wooden(data["area"], result),
        reply_markup=consultation_keyboard(),
        parse_mode="HTML",
    )
    await state.clear()
