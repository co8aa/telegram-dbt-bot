import sys
import os
import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
PORT = int(os.getenv("PORT", 10000))


def main_kb():
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🧘 Навыки"), KeyboardButton(text="📝 Дневник")],
            [KeyboardButton(text="🆘 Кризис"), KeyboardButton(text="📊 Статистика")],
        ],
        resize_keyboard=True,
    )
    return kb


dp = Dispatcher(storage=MemoryStorage())


@dp.message(CommandStart())
async def cmd_start(message: Message):
    logger.info(f"START from {message.from_user.id}")
    await message.answer("Привет! 👋 Выбери раздел:", reply_markup=main_kb())


@dp.message()
async def fallback(message: Message):
    logger.info(f"FALLBACK: {message.text}")
    await message.answer(f"Ты написал: {message.text}\nНажми /start")


async def main():
    bot = Bot(token=BOT_TOKEN)
    if WEBHOOK_URL:
        wh = f"{WEBHOOK_URL}/webhook/{BOT_TOKEN}"
        await bot.set_webhook(wh)
        logger.info(f"Webhook set: {wh}")
        app = web.Application()
        SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=f"/webhook/{BOT_TOKEN}")
        setup_application(app, dp, bot=bot)
        runner = web.AppRunner(app)
        await runner.setup()
        await web.TCPSite(runner, "0.0.0.0", PORT).start()
        logger.info(f"Running on port {PORT}")
        await asyncio.Event().wait()
    else:
        await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
