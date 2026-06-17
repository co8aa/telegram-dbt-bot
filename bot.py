import sys
import os
_dir = os.path.dirname(os.path.abspath(__file__))
if _dir not in sys.path:
    sys.path.insert(0, _dir)

import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from config import BOT_TOKEN, WEBHOOK_URL, PORT
from models.user import init_db
from handlers import start, skills, diary, crisis, stats

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def build_dp() -> Dispatcher:
    dp = Dispatcher(storage=MemoryStorage())
    # start идёт первым — чтобы /start не перехватывался другими
    dp.include_router(start.router)
    dp.include_router(skills.router)
    dp.include_router(diary.router)
    dp.include_router(crisis.router)
    dp.include_router(stats.router)

    @dp.message()
    async def fallback(message: Message):
        await message.answer("Воспользуйся кнопками меню или нажми /start 👇")

    return dp


async def on_startup(bot: Bot):
    init_db()
    if WEBHOOK_URL:
        wh = f"{WEBHOOK_URL}/webhook/{BOT_TOKEN}"
        await bot.set_webhook(wh)
        logger.info(f"Webhook: {wh}")
    else:
        logger.info("Polling mode")


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp  = build_dp()
    await on_startup(bot)

    if WEBHOOK_URL:
        app = web.Application()
        SimpleRequestHandler(dispatcher=dp, bot=bot).register(
            app, path=f"/webhook/{BOT_TOKEN}"
        )
        setup_application(app, dp, bot=bot)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", PORT)
        await site.start()
        logger.info(f"Webhook server on port {PORT}")
        await asyncio.Event().wait()
    else:
        await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
