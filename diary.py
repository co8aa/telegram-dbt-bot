from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from models.user import add_diary_entry
from utils.keyboards import main_kb


class DiaryFSM(StatesGroup):
    emotion = State()
    intensity = State()
    situation = State()
    thoughts = State()
    impulse = State()


async def start_diary(message: types.Message):
    await DiaryFSM.emotion.set()
    await message.answer(
        "📝 *Дневник эмоций*\n\n"
        "Я задам тебе несколько вопросов — это займёт около минуты.\n\n"
        "Какую *эмоцию* ты сейчас чувствуешь? Напиши одним-двумя словами.\n"
        "_(Например: тревога, злость, грусть, стыд, страх, радость...)_",
        parse_mode="Markdown",
    )


async def diary_get_emotion(message: types.Message, state: FSMContext):
    await state.update_data(emotion=message.text.strip())
    kb = InlineKeyboardMarkup(row_width=5)
    kb.add(*[
        InlineKeyboardButton(str(i), callback_data=f"diary_int_{i}")
        for i in range(0, 11)
    ])
    await DiaryFSM.intensity.set()
    await message.answer(
        f"Эмоция: *{message.text.strip()}*\n\n"
        "Оцени её *интенсивность* от 0 до 10:",
        parse_mode="Markdown",
        reply_markup=kb,
    )


async def diary_get_intensity(callback: types.CallbackQuery, state: FSMContext):
    intensity = int(callback.data.replace("diary_int_", ""))
    await state.update_data(intensity=intensity)
    await DiaryFSM.situation.set()
    await callback.message.edit_text(
        f"Интенсивность: *{intensity}/10*\n\n"
        "Что *произошло* прямо перед этим? Опиши ситуацию кратко.",
        parse_mode="Markdown",
    )
    await callback.answer()


async def diary_get_situation(message: types.Message, state: FSMContext):
    await state.update_data(situation=message.text.strip())
    await DiaryFSM.thoughts.set()
    await message.answer(
        "Какие *мысли* пришли вместе с этой эмоцией?\n"
        "_(Что ты подумал(а) о себе, других, ситуации?)_",
        parse_mode="Markdown",
    )


async def diary_get_thoughts(message: types.Message, state: FSMContext):
    await state.update_data(thoughts=message.text.strip())
    await DiaryFSM.impulse.set()
    await message.answer(
        "Что тебе *хотелось сделать* под влиянием этой эмоции?\n"
        "_(Убежать, накричать, закрыться, заплакать...)_",
        parse_mode="Markdown",
    )


async def diary_get_impulse(message: types.Message, state: FSMContext):
    data = await state.get_data()
    impulse = message.text.strip()
    add_diary_entry(
        user_id=message.from_user.id,
        emotion=data["emotion"],
        intensity=data["intensity"],
        situation=data["situation"],
        thoughts=data["thoughts"],
        impulse=impulse,
    )
    await state.finish()
    await message.answer(
        "✅ *Запись сохранена!*\n\n"
        f"📌 Эмоция: {data['emotion']} ({data['intensity']}/10)\n"
        f"📌 Ситуация: {data['situation']}\n"
        f"📌 Мысли: {data['thoughts']}\n"
        f"📌 Импульс: {impulse}\n\n"
        "Осознавание — уже первый шаг. Хочешь попробовать упражнение? "
        "Выбери *Навыки* в меню.",
        parse_mode="Markdown",
        reply_markup=main_kb(),
    )


async def cancel_diary(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Запись отменена.", reply_markup=main_kb())
