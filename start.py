from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from models.user import upsert_user
from utils.keyboards import main_kb

router = Router()

WELCOME = (
    "Привет, {name}\\! 👋\n\n"
    "Я помогу тебе практиковать навыки *Диалектической поведенческой терапии \\(DBT\\)*:\n"
    "• управлять эмоциями\n"
    "• переносить стресс\n"
    "• выстраивать отношения\n"
    "• оставаться в моменте\n\n"
    "⚠️ *Важно:* Этот бот — дополнение к терапии, а не её замена\\. "
    "При серьёзных состояниях обращайтесь к специалисту\\.\n\n"
    "Выбери раздел 👇"
)


@router.message(CommandStart())
async def cmd_start(message: Message):
    user = message.from_user
    upsert_user(user.id, user.username or "", user.first_name or "")
    await message.answer(
        WELCOME.format(name=user.first_name or ""),
        parse_mode="MarkdownV2",
        reply_markup=main_kb(),
    )
