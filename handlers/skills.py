import json
from pathlib import Path
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from utils.keyboards import skills_inline, exercises_inline, next_step_btn, back_to_main_btn

router = Router()

with open(Path(__file__).parent.parent / "data" / "dbt_content.json", encoding="utf-8") as f:
    CONTENT = json.load(f)

SKILLS    = CONTENT["skills"]
EXERCISES = CONTENT["exercises"]


@router.message(F.text == "🧘 Навыки")
async def show_skills_menu(message: Message):
    await message.answer(
        "📚 *Навыки DBT*\n\nВыбери модуль:",
        parse_mode="Markdown",
        reply_markup=skills_inline(SKILLS),
    )


@router.callback_query(F.data.startswith("skill_"))
async def show_skill_detail(callback: CallbackQuery):
    key = callback.data.replace("skill_", "")
    skill = SKILLS.get(key)
    if not skill:
        await callback.answer("Навык не найден")
        return
    text = f"*{skill['title']}*\n\n{skill['description']}"
    kb   = exercises_inline(skill.get("exercises", []), EXERCISES)
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=kb)
    await callback.answer()


@router.callback_query(F.data.startswith("ex_"))
async def exercise_step(callback: CallbackQuery):
    parts    = callback.data.split("_", 2)   # ex, key, step
    key      = parts[1]
    step     = int(parts[2])
    exercise = EXERCISES.get(key)
    if not exercise:
        await callback.answer("Упражнение не найдено")
        return

    steps = exercise["steps"]
    text  = f"*{exercise['title']}*\n\n{steps[step]}"

    kb = next_step_btn(key, step + 1) if step + 1 < len(steps) else back_to_main_btn()
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=kb)
    await callback.answer()


@router.callback_query(F.data == "back_skills")
async def back_to_skills(callback: CallbackQuery):
    await callback.message.edit_text(
        "📚 *Навыки DBT*\n\nВыбери модуль:",
        parse_mode="Markdown",
        reply_markup=skills_inline(SKILLS),
    )
    await callback.answer()
