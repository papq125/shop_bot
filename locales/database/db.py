import aiosqlite
import json

DB_PATH = "shop.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT,
                lang TEXT DEFAULT 'ru',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                emoji TEXT DEFAULT '📦',
                device_type TEXT DEFAULT 'phone',
                active INTEGER DEFAULT 1
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER,
                name TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL,
                status TEXT DEFAULT 'active',
                FOREIGN KEY (category_id) REFERENCES categories(id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                key_value TEXT NOT NULL,
                used INTEGER DEFAULT 0,
                order_id INTEGER DEFAULT NULL,
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                nickname TEXT,
                items TEXT,
                total_price REAL,
                discount INTEGER DEFAULT 0,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS promocodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                discount INTEGER NOT NULL,
                uses_left INTEGER DEFAULT 1,
                active INTEGER DEFAULT 1
            )
        """)
        await db.commit()

        # Демо категорії якщо порожньо
        cursor = await db.execute("SELECT COUNT(*) FROM categories")
        count = (await cursor.fetchone())[0]
        if count == 0:
            await db.executemany(
                "INSERT INTO categories (name, emoji, device_type) VALUES (?, ?, ?)",
                [
                    ("На телефон", "📱", "phone"),
                    ("На компьютер", "💻", "pc"),
                ]
            )
            await db.executemany(
                "INSERT INTO products (category_id, name, description, price, status) VALUES (?, ?, ?, ?, ?)",
                [
                    (1, "Cheat #1 Mobile", "Топовый чит для мобильных игр", 299, "active"),
                    (1, "Cheat #2 Mobile", "Премиум чит с автообновлением", 499, "active"),
                    (2, "Cheat #1 PC", "Чит для ПК версии", 399, "updating"),
                    (2, "Cheat #2 PC", "Профессиональный чит для ПК", 699, "active"),
                ]
            )
            await db.executemany(
                "INSERT INTO keys (product_id, key_value) VALUES (?, ?)",
                [
                    (1, "DEMO-KEY-1111-AAAA"),
                    (1, "DEMO-KEY-2222-BBBB"),
                    (2, "DEMO-KEY-3333-CCCC"),
                    (4, "DEMO-KEY-4444-DDDD"),
                ]
            )
            await db.execute(
                "INSERT INTO promocodes (code, discount, uses_left) VALUES (?, ?, ?)",
                ("DEMO10", 10, 100)
            )
            await db.commit()
            print("✅ Демо данные добавлены")


async def get_or_create_user(user_id, username):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT lang FROM users WHERE id = ?", (user_id,))
        row = await cursor.fetchone()
        if not row:
            await db.execute("INSERT INTO users (id, username) VALUES (?, ?)", (user_id, username))
            await db.commit()
            return None
        return row[0]

async def set_user_lang(user_id, lang):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET lang = ? WHERE id = ?", (lang, user_id))
        await db.commit()

async def get_user_lang(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT lang FROM users WHERE id = ?", (user_id,))
        row = await cursor.fetchone()
        return row[0] if row else "ru"

async def get_categories():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT id, name, emoji, device_type FROM categories WHERE active = 1")
        return await cursor.fetchall()

async def get_products_by_category(category_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT id, name, price, status FROM products WHERE category_id = ?",
            (category_id,)
        )
        return await cursor.fetchall()

async def get_product(product_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT id, name, description, price, status FROM products WHERE id = ?",
            (product_id,)
        )
        return await cursor.fetchone()

async def get_stock_count(product_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT COUNT(*) FROM keys WHERE product_id = ? AND used = 0",
            (product_id,)
        )
        return (await cursor.fetchone())[0]

async def get_key_for_product(product_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT id, key_value FROM keys WHERE product_id = ? AND used = 0 LIMIT 1",
            (product_id,)
        )
        return await cursor.fetchone()

async def mark_key_used(key_id, order_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE keys SET used = 1, order_id = ? WHERE id = ?", (order_id, key_id))
        await db.commit()

async def check_promo(code, user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT id, discount, uses_left FROM promocodes WHERE code = ? AND active = 1",
            (code.upper(),)
        )
        row = await cursor.fetchone()
        if not row:
            return None, "invalid"
        pid, discount, uses_left = row
        if uses_left <= 0:
            return None, "used"
        return discount, "ok"

async def use_promo(code):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE promocodes SET uses_left = uses_left - 1 WHERE code = ?",
            (code.upper(),)
        )
        await db.commit()

async def create_order(user_id, username, nickname, items, total, discount):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO orders (user_id, username, nickname, items, total_price, discount) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, username, nickname, json.dumps(items, ensure_ascii=False), total, discount)
        )
        await db.commit()
        return cursor.lastrowid

async def get_order(order_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
        return await cursor.fetchone()

async def update_order_status(order_id, status):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
        await db.commit()

async def get_all_orders(limit=20):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT id, username, nickname, total_price, status, created_at FROM orders ORDER BY id DESC LIMIT ?",
            (limit,)
        )
        return await cursor.fetchall()

async def add_product(category_id, name, description, price):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO products (category_id, name, description, price) VALUES (?, ?, ?, ?)",
            (category_id, name, description, price)
        )
        await db.commit()
        return cursor.lastrowid

async def add_keys(product_id, keys_list):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executemany(
            "INSERT INTO keys (product_id, key_value) VALUES (?, ?)",
            [(product_id, k.strip()) for k in keys_list if k.strip()]
        )
        await db.commit()

async def add_category(name, emoji, device_type):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO categories (name, emoji, device_type) VALUES (?, ?, ?)",
            (name, emoji, device_type)
        )
        await db.commit()

async def add_promo(code, discount, uses):
    async with aiosqlite.connect(DB_PATH) as db:
        try:
            await db.execute(
                "INSERT INTO promocodes (code, discount, uses_left) VALUES (?, ?, ?)",
                (code.upper(), discount, uses)
            )
            await db.commit()
            return True
        except:
            return False

async def get_all_products():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT p.id, p.name, c.name, p.price, p.status FROM products p JOIN categories c ON p.category_id = c.id"
        )
        return await cursor.fetchall()

async def toggle_product_status(product_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT status FROM products WHERE id = ?", (product_id,))
        row = await cursor.fetchone()
        if row:
            new_status = "updating" if row[0] == "active" else "active"
            await db.execute("UPDATE products SET status = ? WHERE id = ?", (new_status, product_id))
            await db.commit()

async def get_stats():
    async with aiosqlite.connect(DB_PATH) as db:
        users = (await (await db.execute("SELECT COUNT(*) FROM users")).fetchone())[0]
        orders = (await (await db.execute("SELECT COUNT(*) FROM orders WHERE status = 'confirmed'")).fetchone())[0]
        revenue = (await (await db.execute("SELECT SUM(total_price) FROM orders WHERE status = 'confirmed'")).fetchone())[0] or 0
        keys = (await (await db.execute("SELECT COUNT(*) FROM keys WHERE used = 0")).fetchone())[0]
        return users, orders, revenue, keys

async def get_all_user_ids():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT id FROM users")
        rows = await cursor.fetchall()
        return [r[0] for r in rows]
