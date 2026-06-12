import os
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from database.db import get_or_create_user, set_user_lang, get_user_lang, get_all_products
from locales.texts import t

router = Router()

SHOP_NAME = os.getenv("SHOP_NAME", "PREMIUM SHOP")
CHANNEL_URL = os.getenv("CHANNEL_URL", "https://t.me/")

def lang_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"),
        ]
    ])

def main_menu_keyboard(lang):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "catalog"), callback_data="catalog")],
        [
            InlineKeyboardButton(text=t(lang, "my_cart"), callback_data="cart"),
            InlineKeyboardButton(text=t(lang, "promo"), callback_data="promo"),
        ],
        [
            InlineKeyboardButton(text=t(lang, "status"), callback_data="status"),
            InlineKeyboardButton(text=t(lang, "support"), callback_data="support"),
        ],
        [InlineKeyboardButton(text=t(lang, "channel"), url=CHANNEL_URL)],
    ])

WELCOME_BANNER = (
    "━━━━━━━━━━━━━━━━━━━━\n"
    "        ⚡ {shop_name} ⚡\n"
    "━━━━━━━━━━━━━━━━━━━━"
)

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    lang = await get_or_create_user(message.from_user.id, message.from_user.username)

    if not lang:
        await message.answer(
            "🌍 <b>Выберите язык / Choose language:</b>",
            reply_markup=lang_keyboard(),
            parse_mode="HTML"
        )
        return

    await show_main_menu(message, lang)

@router.callback_query(F.data.startswith("lang_"))
async def set_language(callback: CallbackQuery, state: FSMContext):
    lang = callback.data.replace("lang_", "")
    await set_user_lang(callback.from_user.id, lang)
    await callback.message.delete()
    await show_main_menu(callback.message, lang, user_name=callback.from_user.first_name)

async def show_main_menu(message: Message, lang: str, user_name: str = None):
    banner = WELCOME_BANNER.format(shop_name=os.getenv("SHOP_NAME", "PREMIUM SHOP"))
    welcome = t(lang, "welcome", shop_name=os.getenv("SHOP_NAME", "PREMIUM SHOP"))

    text = f"{banner}\n\n{welcome}"

    await message.answer(
        text,
        reply_markup=main_menu_keyboard(lang),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "main_menu")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    lang = await get_user_lang(callback.from_user.id)
    banner = WELCOME_BANNER.format(shop_name=os.getenv("SHOP_NAME", "PREMIUM SHOP"))
    welcome = t(lang, "welcome", shop_name=os.getenv("SHOP_NAME", "PREMIUM SHOP"))
    await callback.message.edit_text(
        f"{banner}\n\n{welcome}",
        reply_markup=main_menu_keyboard(lang),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "status")
async def show_status(callback: CallbackQuery):
    lang = await get_user_lang(callback.from_user.id)
    products = await get_all_products()

    items = ""
    for pid, name, cat, price, status in products:
        emoji = "✅" if status == "active" else "🔄"
        status_text = "Работает" if status == "active" else "Обновляется"
        if lang == "en":
            status_text = "Working" if status == "active" else "Updating"
        items += f"{emoji} <b>{name}</b> — {status_text}\n"

    await callback.message.edit_text(
        t(lang, "status_title", items=items),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "main_menu"), callback_data="main_menu")]
        ]),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "support")
async def show_support(callback: CallbackQuery):
    lang = await get_user_lang(callback.from_user.id)
    support = os.getenv("SUPPORT_USERNAME", "@support")
    await callback.message.edit_text(
        t(lang, "support_text", support=support),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "main_menu"), callback_data="main_menu")]
        ]),
        parse_mode="HTML"
    )
