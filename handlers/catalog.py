from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.db import get_categories, get_products_by_category, get_product, get_stock_count, get_user_lang
from locales.texts import t

router = Router()

@router.callback_query(F.data == "catalog")
async def show_catalog(callback: CallbackQuery):
    lang = await get_user_lang(callback.from_user.id)
    categories = await get_categories()

    buttons = []
    for cid, name, emoji, device_type in categories:
        buttons.append([InlineKeyboardButton(
            text=f"{emoji} {name}",
            callback_data=f"cat_{cid}"
        )])
    buttons.append([InlineKeyboardButton(text=t(lang, "main_menu"), callback_data="main_menu")])

    await callback.message.edit_text(
        t(lang, "catalog_title"),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("cat_"))
async def show_category(callback: CallbackQuery):
    lang = await get_user_lang(callback.from_user.id)
    cat_id = int(callback.data.replace("cat_", ""))
    products = await get_products_by_category(cat_id)

    buttons = []
    for pid, name, price, status in products:
        status_emoji = "✅" if status == "active" else "🔄"
        buttons.append([InlineKeyboardButton(
            text=f"{status_emoji} {name} — {price} руб",
            callback_data=f"product_{pid}"
        )])
    buttons.append([InlineKeyboardButton(text=t(lang, "back"), callback_data="catalog")])

    categories = await get_categories()
    cat_name = next((c[1] for c in categories if c[0] == cat_id), "")

    await callback.message.edit_text(
        t(lang, "choose_product", category=cat_name),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("product_"))
async def show_product(callback: CallbackQuery):
    lang = await get_user_lang(callback.from_user.id)
    product_id = int(callback.data.replace("product_", ""))
    product = await get_product(product_id)

    if not product:
        await callback.answer("Товар не найден", show_alert=True)
        return

    pid, name, description, price, status = product
    stock = await get_stock_count(pid)

    if status == "updating":
        stock_text = "🔄 В обновлении" if lang == "ru" else "🔄 Updating"
    else:
        stock_text = str(stock) if stock > 0 else ("❌ Нет" if lang == "ru" else "❌ None")

    buttons = []
    if status == "active" and stock > 0:
        buttons.append([
            InlineKeyboardButton(text=t(lang, "add_to_cart"), callback_data=f"add_cart_{pid}"),
            InlineKeyboardButton(text=t(lang, "buy_now"), callback_data=f"buy_now_{pid}"),
        ])
    else:
        buttons.append([InlineKeyboardButton(text=t(lang, "out_of_stock"), callback_data="noop")])

    buttons.append([InlineKeyboardButton(text=t(lang, "back"), callback_data=f"cat_back_{pid}")])

    await callback.message.edit_text(
        t(lang, "product_info",
          name=name,
          description=description or "",
          price=price,
          stock=stock_text),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("cat_back_"))
async def back_to_cat(callback: CallbackQuery):
    product_id = int(callback.data.replace("cat_back_", ""))
    from database.db import get_product
    import aiosqlite
    async with aiosqlite.connect("shop.db") as db:
        cursor = await db.execute("SELECT category_id FROM products WHERE id = ?", (product_id,))
        row = await cursor.fetchone()
    if row:
        callback.data = f"cat_{row[0]}"
        await show_category(callback)

@router.callback_query(F.data == "noop")
async def noop(callback: CallbackQuery):
    await callback.answer()
