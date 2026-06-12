from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.db import check_promo, get_user_lang
from locales.texts import t

router = Router()

class PromoStates(StatesGroup):
    waiting_code = State()

@router.callback_query(F.data == "promo")
async def ask_promo(callback: CallbackQuery, state: FSMContext):
    lang = await get_user_lang(callback.from_user.id)
    await state.set_state(PromoStates.waiting_code)
    await callback.message.edit_text(
        t(lang, "enter_promo"),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "cancel"), callback_data="main_menu")]
        ]),
        parse_mode="HTML"
    )

@router.message(PromoStates.waiting_code)
async def process_promo(message: Message, state: FSMContext):
    lang = await get_user_lang(message.from_user.id)
    code = message.text.strip()
    discount, status = await check_promo(code, message.from_user.id)

    if status == "ok":
        await state.update_data(discount=discount, promo_code=code)
        await state.set_state(None)
        await message.answer(
            t(lang, "promo_valid", discount=discount),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=t(lang, "main_menu"), callback_data="main_menu")]
            ]),
            parse_mode="HTML"
        )
    elif status == "used":
        await state.set_state(None)
        await message.answer(t(lang, "promo_used"), parse_mode="HTML")
    else:
        await state.set_state(None)
        await message.answer(t(lang, "promo_invalid"), parse_mode="HTML")
