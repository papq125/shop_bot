import os
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.db import (get_all_orders, add_product, add_keys, add_category,
                          add_promo, get_all_products, toggle_product_status,
                          get_stats, get_all_user_ids, get_categories)

router = Router()

def is_admin(uid):
    return uid == int(os.getenv("ADMIN_CHAT_ID", "0"))

class AdminStates(StatesGroup):
    add_cat_name = State()
    add_cat_emoji = State()
    add_cat_type = State()
    add_product_cat = State()
    add_product_name = State()
    add_product_desc = State()
    add_product_price = State()
    add_keys_product = State()
    add_keys_text = State()
    add_promo_code = State()
    add_promo_discount = State()
    add_promo_uses = State()
    broadcast_text = State()

def admin_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика", callback_data="adm_stats")],
        [
            InlineKeyboardButton(text="➕ Добавить товар", callback_data="adm_add_product"),
            InlineKeyboardButton(text="🔑 Добавить ключи", callback_data="adm_add_keys"),
        ],
        [
            InlineKeyboardButton(text="📁 Категории", callback_data="adm_add_cat"),
            InlineKeyboardButton(text="🎁 Промокод", callback_data="adm_add_promo"),
        ],
        [
            InlineKeyboardButton(text="📋 Заказы", callback_data="adm_orders"),
            InlineKeyboardButton(text="📦 Товары", callback_data="adm_products"),
        ],
        [InlineKeyboardButton(text="📢 Рассылка", callback_data="adm_broadcast")],
    ])

@router.message(Command("admin"))
async def admin_panel(message: Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer("🔧 <b>Админ-панель</b>", reply_markup=admin_keyboard(), parse_mode="HTML")

@router.callback_query(F.data == "adm_stats")
async def admin_stats(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    users, orders, revenue, keys = await get_stats()
    await callback.message.edit_text(
        f"📊 <b>Статистика</b>\n\n"
        f"👥 Пользователей: <b>{users}</b>\n"
        f"✅ Выполнено заказов: <b>{orders}</b>\n"
        f"💰 Выручка: <b>{revenue:.0f} руб</b>\n"
        f"🔑 Ключей в наличии: <b>{keys}</b>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Назад", callback_data="back_admin")]
        ]),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "adm_orders")
async def admin_orders(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    orders = await get_all_orders()
    if not orders:
        text = "📋 Заказов пока нет"
    else:
        text = "📋 <b>Последние заказы:</b>\n\n"
        for oid, username, nick, total, status, created in orders:
            emoji = "✅" if status == "confirmed" else "⏳" if status == "pending" else "❌"
            text += f"{emoji} #{oid} | @{username} | {nick} | {total} руб\n"
    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Назад", callback_data="back_admin")]
        ]),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "adm_products")
async def admin_products(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    products = await get_all_products()
    buttons = []
    for pid, name, cat, price, status in products:
        emoji = "✅" if status == "active" else "🔄"
        buttons.append([InlineKeyboardButton(
            text=f"{emoji} {name} — {price} руб",
            callback_data=f"toggle_{pid}"
        )])
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="back_admin")])
    await callback.message.edit_text(
        "📦 <b>Товары</b>\nНажми чтобы изменить статус:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("toggle_"))
async def toggle_product(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    pid = int(callback.data.replace("toggle_", ""))
    await toggle_product_status(pid)
    await callback.answer("✅ Статус изменён!")
    await admin_products(callback)

# --- Добавить категорию ---
@router.callback_query(F.data == "adm_add_cat")
async def adm_add_cat(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    await state.set_state(AdminStates.add_cat_name)
    await callback.message.edit_text("📁 Введите <b>название категории</b>:", parse_mode="HTML")

@router.message(AdminStates.add_cat_name)
async def adm_cat_name(message: Message, state: FSMContext):
    await state.update_data(cat_name=message.text)
    await state.set_state(AdminStates.add_cat_emoji)
    await message.answer("Введите <b>эмодзи</b> категории (например 📱):", parse_mode="HTML")

@router.message(AdminStates.add_cat_emoji)
async def adm_cat_emoji(message: Message, state: FSMContext):
    await state.update_data(cat_emoji=message.text)
    await state.set_state(AdminStates.add_cat_type)
    await message.answer(
        "Тип устройства:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📱 Телефон", callback_data="cattype_phone")],
            [InlineKeyboardButton(text="💻 ПК", callback_data="cattype_pc")],
        ])
    )

@router.callback_query(F.data.startswith("cattype_"))
async def adm_cat_type(callback: CallbackQuery, state: FSMContext):
    device = callback.data.replace("cattype_", "")
    data = await state.get_data()
    await add_category(data["cat_name"], data["cat_emoji"], device)
    await state.clear()
    await callback.message.edit_text(f"✅ Категория <b>{data['cat_name']}</b> добавлена!", parse_mode="HTML")

# --- Добавить товар ---
@router.callback_query(F.data == "adm_add_product")
async def adm_add_product(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    categories = await get_categories()
    buttons = [[InlineKeyboardButton(text=f"{c[2]} {c[1]}", callback_data=f"selcat_{c[0]}")] for c in categories]
    await state.set_state(AdminStates.add_product_cat)
    await callback.message.edit_text("Выберите категорию:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@router.callback_query(F.data.startswith("selcat_"))
async def adm_product_cat(callback: CallbackQuery, state: FSMContext):
    cat_id = int(callback.data.replace("selcat_", ""))
    await state.update_data(product_cat=cat_id)
    await state.set_state(AdminStates.add_product_name)
    await callback.message.edit_text("Введите <b>название товара</b>:", parse_mode="HTML")

@router.message(AdminStates.add_product_name)
async def adm_product_name(message: Message, state: FSMContext):
    await state.update_data(product_name=message.text)
    await state.set_state(AdminStates.add_product_desc)
    await message.answer("Введите <b>описание</b>:", parse_mode="HTML")

@router.message(AdminStates.add_product_desc)
async def adm_product_desc(message: Message, state: FSMContext):
    await state.update_data(product_desc=message.text)
    await state.set_state(AdminStates.add_product_price)
    await message.answer("Введите <b>цену</b> (только цифры):", parse_mode="HTML")

@router.message(AdminStates.add_product_price)
async def adm_product_price(message: Message, state: FSMContext):
    try:
        price = float(message.text)
    except:
        await message.answer("❌ Введите число!")
        return
    data = await state.get_data()
    pid = await add_product(data["product_cat"], data["product_name"], data["product_desc"], price)
    await state.clear()
    await message.answer(f"✅ Товар <b>{data['product_name']}</b> добавлен! ID: {pid}", parse_mode="HTML")

# --- Добавить ключи ---
@router.callback_query(F.data == "adm_add_keys")
async def adm_add_keys(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    products = await get_all_products()
    buttons = [[InlineKeyboardButton(text=f"{p[1]}", callback_data=f"selp_{p[0]}")] for p in products]
    await state.set_state(AdminStates.add_keys_product)
    await callback.message.edit_text("Выберите товар:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@router.callback_query(F.data.startswith("selp_"))
async def adm_keys_product(callback: CallbackQuery, state: FSMContext):
    pid = int(callback.data.replace("selp_", ""))
    await state.update_data(keys_product=pid)
    await state.set_state(AdminStates.add_keys_text)
    await callback.message.edit_text(
        "Введите ключи (каждый с новой строки):\n\n<code>KEY-1111-AAAA\nKEY-2222-BBBB</code>",
        parse_mode="HTML"
    )

@router.message(AdminStates.add_keys_text)
async def adm_keys_text(message: Message, state: FSMContext):
    data = await state.get_data()
    keys = message.text.strip().split("\n")
    await add_keys(data["keys_product"], keys)
    await state.clear()
    await message.answer(f"✅ Добавлено <b>{len(keys)}</b> ключей!", parse_mode="HTML")

# --- Промокод ---
@router.callback_query(F.data == "adm_add_promo")
async def adm_add_promo(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    await state.set_state(AdminStates.add_promo_code)
    await callback.message.edit_text("Введите <b>код промокода</b> (латиница):", parse_mode="HTML")

@router.message(AdminStates.add_promo_code)
async def adm_promo_code(message: Message, state: FSMContext):
    await state.update_data(promo_code=message.text.upper())
    await state.set_state(AdminStates.add_promo_discount)
    await message.answer("Введите <b>скидку</b> в % (например 10):", parse_mode="HTML")

@router.message(AdminStates.add_promo_discount)
async def adm_promo_discount(message: Message, state: FSMContext):
    try:
        disc = int(message.text)
    except:
        await message.answer("❌ Введите число!")
        return
    await state.update_data(promo_discount=disc)
    await state.set_state(AdminStates.add_promo_uses)
    await message.answer("Сколько раз можно использовать?", parse_mode="HTML")

@router.message(AdminStates.add_promo_uses)
async def adm_promo_uses(message: Message, state: FSMContext):
    try:
        uses = int(message.text)
    except:
        await message.answer("❌ Введите число!")
        return
    data = await state.get_data()
    ok = await add_promo(data["promo_code"], data["promo_discount"], uses)
    await state.clear()
    if ok:
        await message.answer(f"✅ Промокод <code>{data['promo_code']}</code> создан! Скидка: {data['promo_discount']}%", parse_mode="HTML")
    else:
        await message.answer("❌ Такой код уже существует")

# --- Рассылка ---
@router.callback_query(F.data == "adm_broadcast")
async def adm_broadcast(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    await state.set_state(AdminStates.broadcast_text)
    await callback.message.edit_text("📢 Введите текст рассылки:")

@router.message(AdminStates.broadcast_text)
async def adm_broadcast_send(message: Message, state: FSMContext, bot: Bot):
    await state.clear()
    user_ids = await get_all_user_ids()
    sent = 0
    for uid in user_ids:
        try:
            await bot.send_message(uid, message.text, parse_mode="HTML")
            sent += 1
        except:
            pass
    await message.answer(f"✅ Отправлено {sent}/{len(user_ids)} пользователям")

@router.callback_query(F.data == "back_admin")
async def back_admin(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    await callback.message.edit_text("🔧 <b>Админ-панель</b>", reply_markup=admin_keyboard(), parse_mode="HTML")
