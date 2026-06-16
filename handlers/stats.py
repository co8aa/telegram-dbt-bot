from aiogram import Router, F
from aiogram.types import Message
from models.user import get_diary_entries, get_week_stats
from utils.keyboards import main_kb

router = Router()


@router.message(F.text == "📊 Статистика")
async def show_stats(message: Message):
    uid     = message.from_user.id
    entries = get_diary_entries(uid, limit=5)
    week    = get_week_stats(uid)

    if not entries:
        await message.answer(
            "📊 *Статистика*\n\nЗаписей пока нет.\nНачни с раздела *📝 Дневник*.",
            parse_mode="Markdown",
            reply_markup=main_kb(),
        )
        return

    lines = ["📊 *Последние записи:*\n"]
    for row in entries:
        ts = row["timestamp"][:10]
        lines.append(f"• {ts} — *{row['emotion']}* ({row['intensity']}/10): _{row['situation']}_")

    if week:
        lines.append("\n🔝 *Частые эмоции за 7 дней:*")
        for row in week:
            lines.append(f"  {row['emotion']} — {row['cnt']} раз(а)")

    await message.answer("\n".join(lines), parse_mode="Markdown", reply_markup=main_kb())
