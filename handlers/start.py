from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from keyboards.main_kb import main_menu

router = Router()

WELCOME = (
    "👋 Добро пожаловать в <b>BTR Bot</b>!\n\n"
    "Я рассчитаю стоимость работ по укладке полов.\n"
    "💡 Цены только за <b>работу</b>, без материалов.\n\n"
    "Выберите тип пола:"
)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(WELCOME, reply_markup=main_menu(), parse_mode="HTML")


@router.callback_query(F.data == "menu")
async def back_to_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer(WELCOME, reply_markup=main_menu(), parse_mode="HTML")
    await callback.answer()
