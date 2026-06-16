import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext

from config import BOT_TOKEN, WEBHOOK_URL, PORT
from models.user import init_db

from handlers.start import cmd_start
from handlers.skills import (
    show_skills_menu, show_skill_detail, exercise_step, back_to_skills
)
from handlers.diary import (
    DiaryFSM,
    start_diary,
    diary_get_emotion,
    diary_get_intensity,
    diary_get_situation,
    diary_get_thoughts,
    diary_get_impulse,
    cancel_diary,
)
from handlers.crisis import show_crisis, is_crisis_message
from handlers.stats import show_stats

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN, parse_mode="Markdown")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# ── Команды ──────────────────────────────────────────────────────────────────
dp.register_message_handler(cmd_start, commands=["start"], state="*")


# ── Кризисные сообщения (перехватываем до остальных) ─────────────────────────
@dp.message_handler(lambda m: is_crisis_message(m.text or ""), state="*")
async def handle_crisis_keywords(message: types.Message, state: FSMContext):
    await state.finish()
    await show_crisis(message)


# ── Главное меню (текстовые кнопки) ──────────────────────────────────────────
dp.register_message_handler(show_skills_menu, lambda m: m.text == "🧘 Навыки", state="*")
dp.register_message_handler(show_crisis,      lambda m: m.text == "🆘 Кризис",  state="*")
dp.register_message_handler(show_stats,       lambda m: m.text == "📊 Моя статистика", state="*")
dp.register_message_handler(start_diary,      lambda m: m.text == "📝 Дневник", state="*")

# ── Дневник — FSM шаги ───────────────────────────────────────────────────────
dp.register_message_handler(cancel_diary, commands=["cancel"], state="*")
dp.register_message_handler(diary_get_emotion,   state=DiaryFSM.emotion)
dp.register_message_handler(diary_get_situation, state=DiaryFSM.situation)
dp.register_message_handler(diary_get_thoughts,  state=DiaryFSM.thoughts)
dp.register_message_handler(diary_get_impulse,   state=DiaryFSM.impulse)

# ── Callback-кнопки ──────────────────────────────────────────────────────────
dp.register_callback_query_handler(
    show_skill_detail, lambda c: c.data and c.data.startswith("skill_")
)
dp.register_callback_query_handler(
    exercise_step, lambda c: c.data and c.data.startswith("ex_")
)
dp.register_callback_query_handler(
    back_to_skills, lambda c: c.data == "back_skills"
)
dp.register_callback_query_handler(
    diary_get_intensity, lambda c: c.data and c.data.startswith("diary_int_"),
    state=DiaryFSM.intensity,
)


@dp.callback_query_handler(lambda c: c.data == "main_menu", state="*")
async def cb_main_menu(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    from handlers.start import cmd_start as _start
    await callback.message.delete()
    await _start(callback.message)
    await callback.answer()


# ── Fallback ─────────────────────────────────────────────────────────────────
@dp.message_handler(state="*")
async def fallback(message: types.Message):
    await message.answer(
        "Не понял 🤔 Воспользуйся кнопками меню или нажми /start"
    )


# ── Запуск ────────────────────────────────────────────────────────────────────
async def on_startup(dp):
    init_db()
    if WEBHOOK_URL:
        webhook = f"{WEBHOOK_URL}/webhook/{BOT_TOKEN}"
        await bot.set_webhook(webhook)
        logger.info(f"Webhook set: {webhook}")
    else:
        logger.info("Polling mode")


async def on_shutdown(dp):
    if WEBHOOK_URL:
        await bot.delete_webhook()


if __name__ == "__main__":
    if WEBHOOK_URL:
        from aiohttp import web
        from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

        app = web.Application()
        SimpleRequestHandler(
            dispatcher=dp,
            bot=bot,
        ).register(app, path=f"/webhook/{BOT_TOKEN}")
        setup_application(app, dp, bot=bot)
        web.run_app(app, host="0.0.0.0", port=PORT)
    else:
        executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
