from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
)


def main_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add(
        KeyboardButton("🧘 Навыки"),
        KeyboardButton("📝 Дневник"),
        KeyboardButton("🆘 Кризис"),
        KeyboardButton("📊 Моя статистика"),
    )
    return kb


def skills_inline(skills: dict) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=1)
    for key, val in skills.items():
        kb.add(InlineKeyboardButton(val["title"], callback_data=f"skill_{key}"))
    return kb


def exercises_inline(exercise_keys: list, exercises: dict) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=1)
    for key in exercise_keys:
        ex = exercises.get(key)
        if ex:
            kb.add(InlineKeyboardButton(ex["title"], callback_data=f"ex_{key}_0"))
    kb.add(InlineKeyboardButton("◀️ К списку навыков", callback_data="back_skills"))
    return kb


def next_step_btn(ex_key: str, step_idx: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("➡️ Далее", callback_data=f"ex_{ex_key}_{step_idx}"))
    return kb


def back_to_main_btn() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu"))
    return kb


def rating_kb(prefix: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=5)
    kb.add(*[
        InlineKeyboardButton(str(i), callback_data=f"{prefix}_{i}")
        for i in range(1, 6)
    ])
    return kb
