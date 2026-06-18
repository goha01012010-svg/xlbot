import aiosqlite
from datetime import datetime

from config import DB_PATH, DEFAULT_REWARD

# Каналы-задания, добавленные изначально
SEED_CHANNELS = [
    (-1003594114095, "https://t.me/+ivQsuvnsmh4xNDAy", "Канал 1"),
    (-1003693383185, "https://t.me/+e-xhMMTMondiZmNi", "Канал 2"),
    (-1003983524031, "https://t.me/+0AfWmwBQTcU2NGEy", "Канал 3"),
]


async def init_db():
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                reg_date TEXT NOT NULL,
                balance INTEGER NOT NULL DEFAULT 0,
                completed_tasks INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER UNIQUE NOT NULL,
                invite_link TEXT,
                title TEXT,
                reward INTEGER NOT NULL DEFAULT 20,
                active INTEGER NOT NULL DEFAULT 1
            )
            """
        )
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS user_progress (
                user_id INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                completed INTEGER NOT NULL DEFAULT 0,
                completed_at TEXT,
                PRIMARY KEY (user_id, channel_id)
            )
            """
        )
        for chat_id, link, title in SEED_CHANNELS:
            await conn.execute(
                """
                INSERT OR IGNORE INTO channels (chat_id, invite_link, title, reward, active)
                VALUES (?, ?, ?, ?, 1)
                """,
                (chat_id, link, title, DEFAULT_REWARD),
            )
        await conn.commit()


# ---------- USERS ----------

async def get_or_create_user(user_id: int, username: str | None):
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cur = await conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = await cur.fetchone()
        if row:
            await conn.execute(
                "UPDATE users SET username = ? WHERE user_id = ?", (username, user_id)
            )
            await conn.commit()
            return dict(row)
        reg_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        await conn.execute(
            "INSERT INTO users (user_id, username, reg_date, balance, completed_tasks) VALUES (?, ?, ?, 0, 0)",
            (user_id, username, reg_date),
        )
        await conn.commit()
        return {
            "user_id": user_id,
            "username": username,
            "reg_date": reg_date,
            "balance": 0,
            "completed_tasks": 0,
        }


async def get_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cur = await conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = await cur.fetchone()
        return dict(row) if row else None


async def add_balance(user_id: int, amount: int):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id)
        )
        await conn.commit()


async def increment_completed_tasks(user_id: int):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "UPDATE users SET completed_tasks = completed_tasks + 1 WHERE user_id = ?",
            (user_id,),
        )
        await conn.commit()


# ---------- CHANNELS / TASKS ----------

async def get_active_channels():
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cur = await conn.execute(
            "SELECT * FROM channels WHERE active = 1 ORDER BY id"
        )
        rows = await cur.fetchall()
        return [dict(r) for r in rows]


async def add_channel(chat_id: int, invite_link: str, title: str, reward: int):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            """
            INSERT INTO channels (chat_id, invite_link, title, reward, active)
            VALUES (?, ?, ?, ?, 1)
            ON CONFLICT(chat_id) DO UPDATE SET
                invite_link = excluded.invite_link,
                title = excluded.title,
                reward = excluded.reward,
                active = 1
            """,
            (chat_id, invite_link, title, reward),
        )
        await conn.commit()


async def deactivate_channel(channel_db_id: int):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "UPDATE channels SET active = 0 WHERE id = ?", (channel_db_id,)
        )
        await conn.commit()


# ---------- PROGRESS ----------

async def is_channel_completed(user_id: int, channel_db_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as conn:
        cur = await conn.execute(
            "SELECT completed FROM user_progress WHERE user_id = ? AND channel_id = ?",
            (user_id, channel_db_id),
        )
        row = await cur.fetchone()
        return bool(row and row[0])


async def mark_completed(user_id: int, channel_db_id: int):
    completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            """
            INSERT INTO user_progress (user_id, channel_id, completed, completed_at)
            VALUES (?, ?, 1, ?)
            ON CONFLICT(user_id, channel_id) DO UPDATE SET completed = 1, completed_at = excluded.completed_at
            """,
            (user_id, channel_db_id, completed_at),
        )
        await conn.commit()
