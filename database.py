import aiosqlite
from datetime import datetime, timedelta
import random

DB_PATH = "sborshik.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                balance INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                xp INTEGER DEFAULT 0,
                applications_today INTEGER DEFAULT 0,
                last_collect TIMESTAMP,
                last_reset_date TEXT,
                total_collected INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS equipment (
                user_id INTEGER PRIMARY KEY,
                gloves INTEGER DEFAULT 0,
                clothes INTEGER DEFAULT 0,
                tablet INTEGER DEFAULT 0,
                marker_basic INTEGER DEFAULT 0,
                marker_pro INTEGER DEFAULT 0,
                marker_legend INTEGER DEFAULT 0,
                costume INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS businesses (
                user_id INTEGER,
                business_id INTEGER,
                purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, business_id)
            )
        """)
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS investments (
                user_id INTEGER,
                investment_type TEXT,
                amount INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, investment_type)
            )
        """)
        
        await db.commit()


async def get_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def create_user(user_id: int, username: str, full_name: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id, username, full_name, last_reset_date) VALUES (?, ?, ?, ?)",
            (user_id, username, full_name, datetime.now().strftime("%Y-%m-%d"))
        )
        await db.execute(
            "INSERT OR IGNORE INTO equipment (user_id) VALUES (?)",
            (user_id,)
        )
        await db.commit()


async def update_balance(user_id: int, amount: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET balance = balance + ? WHERE user_id = ?",
            (amount, user_id)
        )
        await db.commit()


async def set_balance(user_id: int, amount: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET balance = ? WHERE user_id = ?",
            (amount, user_id)
        )
        await db.commit()


async def get_equipment(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM equipment WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def buy_equipment(user_id: int, item: str, price: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            if not row or row[0] < price:
                return False
        
        await db.execute(f"UPDATE equipment SET {item} = 1 WHERE user_id = ?", (user_id,))
        await db.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (price, user_id))
        await db.commit()
        return True


async def add_xp(user_id: int, xp: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET xp = xp + ? WHERE user_id = ?", (xp, user_id))
        await db.commit()
        
        user = await get_user(user_id)
        levels_xp = [0, 300, 800, 1800, 3500, 6000, 10000, 16000, 25000, 40000]
        
        new_level = user["level"]
        for i, required in enumerate(levels_xp):
            if user["xp"] >= required:
                new_level = i + 1
        
        if new_level > user["level"]:
            await db.execute("UPDATE users SET level = ? WHERE user_id = ?", (new_level, user_id))
            await db.commit()
            return new_level
        return None


async def can_collect(user_id: int) -> tuple[bool, str]:
    user = await get_user(user_id)
    if not user:
        return False, "Сначала нажми /start"
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    if user["last_reset_date"] != today:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "UPDATE users SET applications_today = 0, last_reset_date = ? WHERE user_id = ?",
                (today, user_id)
            )
            await db.commit()
        user["applications_today"] = 0
    
    if user["applications_today"] >= 40:
        return False, "Ты уже собрал максимум 40 заявок на сегодня. Приходи завтра!"
    
    if user["last_collect"]:
        last = datetime.fromisoformat(user["last_collect"])
        if datetime.now() - last < timedelta(seconds=120):
            remaining = 120 - int((datetime.now() - last).total_seconds())
            return False, f"Подожди ещё {remaining} сек. перед следующей заявкой"
    
    return True, "ok"


async def collect_application(user_id: int) -> dict:
    from config import MIN_APPLICATION_PRICE, MAX_APPLICATION_PRICE
    
    can, msg = await can_collect(user_id)
    if not can:
        return {"success": False, "message": msg}
    
    eq = await get_equipment(user_id)
    user = await get_user(user_id)
    
    price_bonus = 0
    if eq:
        if eq["clothes"]: price_bonus += 7
        if eq["marker_basic"]: price_bonus += 5
        if eq["marker_pro"]: price_bonus += 9
        if eq["marker_legend"]: price_bonus += 10
        if eq["costume"]: price_bonus += 50
    
    base_price = random.randint(MIN_APPLICATION_PRICE, MAX_APPLICATION_PRICE)
    final_price = int(base_price * (1 + price_bonus / 100))
    
    xp_gain = random.randint(8, 25)
    if eq and eq["tablet"]:
        xp_gain = int(xp_gain * 1.08)
    
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE users 
            SET balance = balance + ?,
                applications_today = applications_today + 1,
                last_collect = ?,
                total_collected = total_collected + 1,
                xp = xp + ?
            WHERE user_id = ?
        """, (final_price, datetime.now().isoformat(), xp_gain, user_id))
        await db.commit()
    
    new_level = await add_xp(user_id, 0)
    
    return {
        "success": True,
        "price": final_price,
        "xp": xp_gain,
        "new_level": new_level,
        "applications_today": user["applications_today"] + 1
    }


async def get_top_players(limit: int = 10):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT user_id, username, full_name, balance, level, total_collected
            FROM users
            ORDER BY balance DESC
            LIMIT ?
        """, (limit,)) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]


async def get_user_rank(user_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT COUNT(*) + 1 as rank
            FROM users
            WHERE balance > (SELECT balance FROM users WHERE user_id = ?)
        """, (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 1
