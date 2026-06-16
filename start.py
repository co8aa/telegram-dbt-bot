from aiogram import types
from models.user import upsert_user
from utils.keyboards import main_kb

DISCLAIMER = (
    "⚠️ *Важно:* Этот бот — дополнение к терапии, а не её замена. "
    "При серьёзных состояниях, пожалуйста, обращайтесь к специалисту."
)

WELCOME = (
    "Привет, {name}! 👋\n\n"
    "Я помогу тебе практиковать навыки *Диалектической поведенческой терапии (DBT)*:\n"
    "• управлять эмоциями\n"
    "• переносить стресс\n"
    "• выстраивать отношения\n"
    "• оставаться в моменте\n\n"
    f"{DISCLAIMER}\n\n"
    "Выбери раздел 👇"
)


async def cmd_start(message: types.Message):
    user = message.from_user
    upsert_user(user.id, user.username or "", user.first_name or "")
    await message.answer(
        WELCOME.format(name=user.first_name or ""),
        parse_mode="Markdown",
        reply_markup=main_kb(),
    )
