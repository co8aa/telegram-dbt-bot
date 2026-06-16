from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from models.user import upsert_user
from utils.keyboards import main_kb

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    user = message.from_user
    upsert_user(user.id, user.username or "", user.first_name or "")
    await message.answer(
        "Привет! 👋\n\n"
        "Я помогу практиковать навыки DBT:\n"
        "• управлять эмоциями\n"
        "• переносить стресс\n"
        "• выстраивать отношения\n\n"
        "⚠️ Бот — дополнение к терапии, не её замена.\n\n"
        "Выбери раздел 👇",
        reply_markup=main_kb(),
    )
