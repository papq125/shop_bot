import os
import json
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.db import (create_order, get_key_for_product, mark_key_used,
                          update_order_status, get_user_lang)
from locales.texts import t

router = Router()

class CheckoutStates(StatesGroup):
    waiting_nick = State()
    waiting_screenshot = State()

@router.callback_query(F.data == "checkout")
async def start_checkout(callback: CallbackQuery, state: FSMContext):
    lang = await get_user_lang(callback.from_user.id)
    data = await state.get_data()
    cart = data.get("cart", {})
    if not cart:
        await callback.answer("Корзина пуста!", show_alert=True)
        return
    await state.set_state(CheckoutStates.waiting_nick)
    await callback.message.edit_text(
        t(lang, "enter_nick"),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "cancel"), callback_data="main_menu")]
        ]),
        parse_mode="HTML"
    )

@router.message(CheckoutStates.waiting_nick)
async def process_nick(message: Message, state: FSMContext):
    lang = await get_user_lang(message.from_user.id)
    await state.update_data(nickname=message.text)
    await state.set_state(CheckoutStates.waiting_screenshot)

    data = await state.get_data()
    cart = data.get("cart", {})
    discount = data.get("discount", 0)

    total = sum(i["price"] * i["quantity"] for i in cart.values())
    if discount > 0:
        total = total * (1 - discount / 100)

    items_text = "\n".join([
        f"▪️ {i['name']} x{i['quantity']} = {i['price'] * i['quantity']} руб"
        for i in cart.values()
    ])

    card = os.getenv("MONO_CARD", "0000 0000 0000 0000")

    await message.answer(
        t(lang, "payment_info",
          items=items_text,
          total=int(total),
          card=card),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "cancel"), callback_data="main_menu")]
        ]),
        parse_mode="HTML"
    )

@router.message(CheckoutStates.waiting_screenshot, F.photo)
async def process_screenshot(message: Message, state: FSMContext, bot: Bot):
    lang = await get_user_lang(message.from_user.id)
    data = await state.get_data()
    cart = data.get("cart", {})
    discount = data.get("discount", 0)
    nickname = data.get("nickname", "—")
    promo_code = data.get("promo_code")

    total = sum(i["price"] * i["quantity"] for i in cart.values())
    if discount > 0:
        total = total * (1 - discount / 100)

    order_id = await create_order(
        user_id=message.from_user.id,
        username=message.from_user.username or "—",
        nickname=nickname,
        items=cart,
        total=int(total),
        discount=discount
    )

    if promo_code:
        from database.db import use_promo
        await use_promo(promo_code)

    items_text = "\n".join([
        f"▪️ {i['name']} x{i['quantity']} = {i['price'] * i['quantity']} руб"
        for i in cart.values()
    ])

    admin_id = int(os.getenv("ADMIN_CHAT_ID", "0"))
    admin_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"confirm_{order_id}_{message.from_user.id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{order_id}_{message.from_user.id}"),
        ],
        [InlineKeyboardButton(text="⚡ Выдать ключ авто", callback_data=f"autokey_{order_id}_{message.from_user.id}")]
    ])

    if admin_id:
        await bot.send_photo(
            chat_id=admin_id,
            photo=message.photo[-1].file_id,
            caption=(
                f"🔔 <b>НОВЫЙ ЗАКАЗ #{order_id}</b>\n\n"
                f"👤 @{message.from_user.username or '—'} (ID: {message.from_user.id})\n"
                f"🎮 Никнейм: <b>{nickname}</b>\n"
                f"🎁 Промокод: {promo_code or '—'} ({discount}%)\n\n"
                f"<b>Товары:</b>\n{items_text}\n\n"
                f"💰 <b>Сумма: {int(total)} руб</b>"
            ),
            reply_markup=admin_keyboard,
            parse_mode="HTML"
        )

    await state.clear()
    await message.answer(
        t(lang, "order_sent", order_id=order_id),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "main_menu"), callback_data="main_menu")]
        ]),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("confirm_"))
async def confirm_order(callback: CallbackQuery, bot: Bot):
    parts = callback.data.split("_")
    order_id, customer_id = int(parts[1]), int(parts[2])
    await update_order_status(order_id, "confirmed")

    from database.db import get_order
    order = await get_order(order_id)
    if order:
        items = json.loads(order[4])
        keys_text = ""
        for pid_str, item in items.items():
            key_row = await get_key_for_product(int(pid_str))
            if key_row:
                await mark_key_used(key_row[0], order_id)
                keys_text += f"🔑 <b>{item['name']}:</b>\n<code>{key_row[1]}</code>\n\n"
            else:
                keys_text += f"⚠️ <b>{item['name']}:</b> ключ отсутствует\n\n"

        lang = await get_user_lang(customer_id)
        await bot.send_message(
            chat_id=customer_id,
            text=(
                f"🎉 <b>Заказ #{order_id} выполнен!</b>\n\n"
                f"{keys_text}"
                f"Спасибо за покупку! 🏆"
            ),
            parse_mode="HTML"
        )

    await callback.message.edit_caption(
        callback.message.caption + "\n\n✅ <b>ПОДТВЕРЖДЕНО — ключи выданы</b>",
        parse_mode="HTML"
    )
    await callback.answer("✅ Подтверждено!")

@router.callback_query(F.data.startswith("reject_"))
async def reject_order(callback: CallbackQuery, bot: Bot):
    parts = callback.data.split("_")
    order_id, customer_id = int(parts[1]), int(parts[2])
    await update_order_status(order_id, "rejected")
    lang = await get_user_lang(customer_id)
    await bot.send_message(customer_id, t(lang, "order_rejected"), parse_mode="HTML")
    await callback.message.edit_caption(
        callback.message.caption + "\n\n❌ <b>ОТКЛОНЕНО</b>",
        parse_mode="HTML"
    )
    await callback.answer("❌ Отклонено")

@router.callback_query(F.data.startswith("autokey_"))
async def auto_key(callback: CallbackQuery, bot: Bot):
    parts = callback.data.split("_")
    order_id, customer_id = int(parts[1]), int(parts[2])
    await confirm_order(callback, bot)
