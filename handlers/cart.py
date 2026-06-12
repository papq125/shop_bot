from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from database.db import get_product, get_stock_count, get_user_lang
from locales.texts import t

router = Router()

def cart_keyboard(lang, cart, has_promo=False):
    buttons = []
    for pid, item in cart.items():
        buttons.append([InlineKeyboardButton(
            text=f"❌ {item['name']}",
            callback_data=f"remove_{pid}"
        )])
    if cart:
        buttons.append([InlineKeyboardButton(text=t(lang, "checkout"), callback_data="checkout")])
        buttons.append([InlineKeyboardButton(text=t(lang, "clear_cart"), callback_data="clear_cart")])
    buttons.append([InlineKeyboardButton(text=t(lang, "main_menu"), callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def cart_text(lang, cart, discount=0):
    if not cart:
        return t(lang, "cart_empty")
    items = ""
    total = 0
    for pid, item in cart.items():
        sub = item['price'] * item['quantity']
        items += f"▪️ {item['name']} x{item['quantity']} = <b>{sub} руб</b>\n"
        total += sub
    if discount > 0:
        discounted = total * (1 - discount / 100)
        items += f"\n🎁 Скидка {discount}%: <s>{total}</s> → <b>{discounted:.0f} руб</b>"
        total = discounted
    return t(lang, "cart_title", items=items, total=int(total))

@router.callback_query(F.data == "cart")
async def show_cart(callback: CallbackQuery, state: FSMContext):
    lang = await get_user_lang(callback.from_user.id)
    data = await state.get_data()
    cart = data.get("cart", {})
    discount = data.get("discount", 0)
    await callback.message.edit_text(
        cart_text(lang, cart, discount),
        reply_markup=cart_keyboard(lang, cart),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("add_cart_"))
async def add_to_cart(callback: CallbackQuery, state: FSMContext):
    lang = await get_user_lang(callback.from_user.id)
    product_id = int(callback.data.replace("add_cart_", ""))
    product = await get_product(product_id)
    if not product:
        await callback.answer("Не найдено", show_alert=True)
        return

    pid, name, desc, price, status = product
    stock = await get_stock_count(pid)
    if stock == 0:
        await callback.answer(t(lang, "out_of_stock"), show_alert=True)
        return

    data = await state.get_data()
    cart = data.get("cart", {})
    str_id = str(product_id)
    if str_id in cart:
        cart[str_id]["quantity"] += 1
    else:
        cart[str_id] = {"name": name, "price": price, "quantity": 1}
    await state.update_data(cart=cart)
    await callback.answer(t(lang, "added_to_cart"))

@router.callback_query(F.data.startswith("buy_now_"))
async def buy_now(callback: CallbackQuery, state: FSMContext):
    lang = await get_user_lang(callback.from_user.id)
    product_id = int(callback.data.replace("buy_now_", ""))
    product = await get_product(product_id)
    if not product:
        return
    pid, name, desc, price, status = product
    cart = {str(pid): {"name": name, "price": price, "quantity": 1}}
    await state.update_data(cart=cart)
    callback.data = "checkout"
    from handlers.checkout import start_checkout
    await start_checkout(callback, state)

@router.callback_query(F.data.startswith("remove_"))
async def remove_from_cart(callback: CallbackQuery, state: FSMContext):
    lang = await get_user_lang(callback.from_user.id)
    pid = callback.data.replace("remove_", "")
    data = await state.get_data()
    cart = data.get("cart", {})
    if pid in cart:
        del cart[pid]
        await state.update_data(cart=cart)
    discount = data.get("discount", 0)
    await callback.message.edit_text(
        cart_text(lang, cart, discount),
        reply_markup=cart_keyboard(lang, cart),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "clear_cart")
async def clear_cart(callback: CallbackQuery, state: FSMContext):
    lang = await get_user_lang(callback.from_user.id)
    await state.update_data(cart={}, discount=0, promo_code=None)
    await callback.message.edit_text(
        t(lang, "cart_empty"),
        reply_markup=cart_keyboard(lang, {}),
        parse_mode="HTML"
    )
