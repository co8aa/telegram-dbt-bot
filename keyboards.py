from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def main_kb() -> ReplyKeyboardMarkup:
    b = ReplyKeyboardBuilder()
    b.row(KeyboardButton(text="🧘 Навыки"),    KeyboardButton(text="📝 Дневник"))
    b.row(KeyboardButton(text="🆘 Кризис"),    KeyboardButton(text="📊 Статистика"))
    return b.as_markup(resize_keyboard=True)


def skills_inline(skills: dict) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for key, val in skills.items():
        b.button(text=val["title"], callback_data=f"skill_{key}")
    b.adjust(1)
    return b.as_markup()


def exercises_inline(exercise_keys: list, exercises: dict) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for key in exercise_keys:
        ex = exercises.get(key)
        if ex:
            b.button(text=ex["title"], callback_data=f"ex_{key}_0")
    b.button(text="◀️ К списку навыков", callback_data="back_skills")
    b.adjust(1)
    return b.as_markup()


def next_step_btn(ex_key: str, step_idx: int) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="➡️ Далее", callback_data=f"ex_{ex_key}_{step_idx}")
    return b.as_markup()


def back_to_main_btn() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="🏠 Главное меню", callback_data="main_menu")
    return b.as_markup()


def intensity_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for i in range(0, 11):
        b.button(text=str(i), callback_data=f"diary_int_{i}")
    b.adjust(6, 5)
    return b.as_markup()
