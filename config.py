import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "ВСТАВЬ_СВОЙ_ТОКЕН_СЮДА")
ADMIN_ID = 952952583

# Игровые константы
MAX_APPLICATIONS_PER_DAY = 40
COLLECT_INTERVAL_SECONDS = 120
MIN_APPLICATION_PRICE = 50
MAX_APPLICATION_PRICE = 5000
