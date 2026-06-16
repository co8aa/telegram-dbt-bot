from aiogram import types
from models.user import get_diary_entries, get_week_stats
from utils.keyboards import main_kb


async def show_stats(message: types.Message):
    user_id = message.from_user.id
    entries = get_diary_entries(user_id, limit=5)
    week = get_week_stats(user_id)

    if not entries:
        await message.answer(
            "📊 *Статистика*\n\nУ тебя пока нет записей в дневнике.\n"
            "Начни отслеживать эмоции через раздел *📝 Дневник*.",
            parse_mode="Markdown",
            reply_markup=main_kb(),
        )
        return

    lines = ["📊 *Твои последние записи:*\n"]
    for row in entries:
        ts = row["timestamp"][:10]
        lines.append(f"• {ts} — *{row['emotion']}* ({row['intensity']}/10): _{row['situation']}_")

    if week:
        lines.append("\n🔝 *Частые эмоции за 7 дней:*")
        for row in week:
            lines.append(f"  {row['emotion']} — {row['cnt']} раз(а)")

    await message.answer("\n".join(lines), parse_mode="Markdown", reply_markup=main_kb())
