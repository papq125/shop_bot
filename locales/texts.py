# Тексти на двох мовах

TEXTS = {
    "ru": {
        "choose_lang": "🌍 Выберите язык / Choose language:",
        "welcome": (
            "⚡ <b>Добро пожаловать в {shop_name}!</b>\n\n"
            "🏆 Лучший магазин софта\n"
            "🔑 Мгновенная выдача ключей\n"
            "💬 Поддержка 24/7\n\n"
            "Выберите действие 👇"
        ),
        "catalog": "🛒 Каталог",
        "my_cart": "🛍 Корзина",
        "promo": "🎁 Промокод",
        "status": "⚡ Статус товаров",
        "support": "💬 Поддержка",
        "channel": "📢 Наш канал",
        "catalog_title": "🛒 <b>Каталог товаров</b>\n\nВыберите категорию:",
        "choose_product": "📦 <b>{category}</b>\n\nВыберите товар:",
        "product_info": (
            "🔥 <b>{name}</b>\n\n"
            "📝 {description}\n\n"
            "💰 Цена: <b>{price} руб</b>\n"
            "🔑 Ключей в наличии: <b>{stock}</b>\n\n"
            "Добавить в корзину?"
        ),
        "add_to_cart": "➕ Добавить в корзину",
        "buy_now": "⚡ Купить сейчас",
        "back": "◀️ Назад",
        "main_menu": "🏠 Главное меню",
        "added_to_cart": "✅ Добавлено в корзину!",
        "out_of_stock": "❌ Нет в наличии",
        "cart_empty": "🛍 <b>Корзина пуста</b>\n\nДобавьте товары из каталога!",
        "cart_title": "🛍 <b>Ваша корзина:</b>\n\n{items}\n\n💰 <b>Итого: {total} руб</b>",
        "checkout": "✅ Оформить заказ",
        "clear_cart": "🗑 Очистить",
        "enter_promo": "🎁 Введите промокод:",
        "promo_valid": "✅ Промокод применён! Скидка {discount}%",
        "promo_invalid": "❌ Неверный промокод",
        "promo_used": "❌ Промокод уже использован",
        "enter_nick": "👤 Введите ваш <b>никнейм</b> (для передачи товара):",
        "payment_info": (
            "💳 <b>Оплата заказа</b>\n\n"
            "{items}\n\n"
            "💰 <b>К оплате: {total} руб</b>\n\n"
            "━━━━━━━━━━━━━━━\n"
            "Переводи на карту:\n"
            "<code>{card}</code>\n"
            "━━━━━━━━━━━━━━━\n\n"
            "После оплаты отправь <b>скриншот чека</b> 📸"
        ),
        "send_screenshot": "📸 Отправьте скриншот оплаты",
        "order_sent": (
            "✅ <b>Заказ #{order_id} принят!</b>\n\n"
            "Проверяем оплату...\n"
            "Обычно это занимает до <b>15 минут</b>\n\n"
            "Ожидайте ключ активации! 🔑"
        ),
        "key_delivered": (
            "🎉 <b>Ваш заказ #{order_id} выполнен!</b>\n\n"
            "🔑 <b>Ключ активации:</b>\n"
            "<code>{key}</code>\n\n"
            "Спасибо за покупку! 🏆"
        ),
        "order_rejected": "❌ Оплата не подтверждена. Обратитесь в поддержку.",
        "status_title": "⚡ <b>Статус товаров:</b>\n\n{items}",
        "status_ok": "✅",
        "status_update": "🔄 Обновляется",
        "support_text": "💬 <b>Поддержка</b>\n\nПишите: {support}",
        "cancel": "❌ Отмена",
    },
    "en": {
        "choose_lang": "🌍 Выберите язык / Choose language:",
        "welcome": (
            "⚡ <b>Welcome to {shop_name}!</b>\n\n"
            "🏆 Best software shop\n"
            "🔑 Instant key delivery\n"
            "💬 Support 24/7\n\n"
            "Choose action 👇"
        ),
        "catalog": "🛒 Catalog",
        "my_cart": "🛍 Cart",
        "promo": "🎁 Promo code",
        "status": "⚡ Product status",
        "support": "💬 Support",
        "channel": "📢 Our channel",
        "catalog_title": "🛒 <b>Product catalog</b>\n\nChoose category:",
        "choose_product": "📦 <b>{category}</b>\n\nChoose product:",
        "product_info": (
            "🔥 <b>{name}</b>\n\n"
            "📝 {description}\n\n"
            "💰 Price: <b>{price} rub</b>\n"
            "🔑 In stock: <b>{stock}</b>\n\n"
            "Add to cart?"
        ),
        "add_to_cart": "➕ Add to cart",
        "buy_now": "⚡ Buy now",
        "back": "◀️ Back",
        "main_menu": "🏠 Main menu",
        "added_to_cart": "✅ Added to cart!",
        "out_of_stock": "❌ Out of stock",
        "cart_empty": "🛍 <b>Cart is empty</b>\n\nAdd products from catalog!",
        "cart_title": "🛍 <b>Your cart:</b>\n\n{items}\n\n💰 <b>Total: {total} rub</b>",
        "checkout": "✅ Checkout",
        "clear_cart": "🗑 Clear",
        "enter_promo": "🎁 Enter promo code:",
        "promo_valid": "✅ Promo applied! Discount {discount}%",
        "promo_invalid": "❌ Invalid promo code",
        "promo_used": "❌ Promo code already used",
        "enter_nick": "👤 Enter your <b>nickname</b> (for delivery):",
        "payment_info": (
            "💳 <b>Payment</b>\n\n"
            "{items}\n\n"
            "💰 <b>Total: {total} rub</b>\n\n"
            "━━━━━━━━━━━━━━━\n"
            "Transfer to card:\n"
            "<code>{card}</code>\n"
            "━━━━━━━━━━━━━━━\n\n"
            "After payment send <b>payment screenshot</b> 📸"
        ),
        "send_screenshot": "📸 Send payment screenshot",
        "order_sent": (
            "✅ <b>Order #{order_id} received!</b>\n\n"
            "Checking payment...\n"
            "Usually takes up to <b>15 minutes</b>\n\n"
            "Wait for activation key! 🔑"
        ),
        "key_delivered": (
            "🎉 <b>Order #{order_id} completed!</b>\n\n"
            "🔑 <b>Activation key:</b>\n"
            "<code>{key}</code>\n\n"
            "Thank you! 🏆"
        ),
        "order_rejected": "❌ Payment not confirmed. Contact support.",
        "status_title": "⚡ <b>Product status:</b>\n\n{items}",
        "status_ok": "✅",
        "status_update": "🔄 Updating",
        "support_text": "💬 <b>Support</b>\n\nContact: {support}",
        "cancel": "❌ Cancel",
    }
}

def t(lang: str, key: str, **kwargs) -> str:
    text = TEXTS.get(lang, TEXTS["ru"]).get(key, key)
    if kwargs:
        try:
            text = text.format(**kwargs)
        except:
            pass
    return text
