import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не задан. Укажите его в файле .env")

_admin_ids_raw = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = {int(x) for x in _admin_ids_raw.replace(" ", "").split(",") if x}

DB_PATH = os.getenv("DB_PATH", "bot.db")

DEFAULT_REWARD = 20   # звёзд за подписку на 1 канал
WITHDRAW_MIN = 200    # минимальный баланс для вывода
