import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")  # https://your-app.onrender.com
PORT = int(os.getenv("PORT", 8000))
DATABASE_URL = os.getenv("DATABASE_URL", "dbt_bot.db")

# Render использует переменные окружения — токен и webhook задаются там
