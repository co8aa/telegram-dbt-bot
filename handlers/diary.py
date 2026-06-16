from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from models.user import add_diary_entry
from utils.keyboards import main_kb, intensity_kb

router = Router()


class DiaryFSM(StatesGroup):
    emotion   = State()
    intensity = State()
    situation = State()
    thoughts  = State()
    impulse   = State()


@router.message(F.text == "📝 Дневник")
async def start_diary(message: Message, state: FSMContext):
    await state.set_state(DiaryFSM.emotion)
    await message.answer(
        "📝 *Дневник эмоций*\n\n"
        "Я задам несколько вопросов — займёт около минуты.\n\n"
        "Какую *эмоцию* ты сейчас чувствуешь? Напиши одним словом.\n"
        "_(Например: тревога, злость, грусть, стыд, страх...)_",
        parse_mode="Markdown",
    )


@router.message(DiaryFSM.emotion)
async def diary_emotion(message: Message, state: FSMContext):
    await state.update_data(emotion=message.text.strip())
    await state.set_state(DiaryFSM.intensity)
    await message.answer(
        f"Эмоция: *{message.text.strip()}*\n\nОцени её *интенсивность* от 0 до 10:",
        parse_mode="Markdown",
        reply_markup=intensity_kb(),
    )


@router.callback_query(F.data.startswith("diary_int_"), DiaryFSM.intensity)
async def diary_intensity(callback: CallbackQuery, state: FSMContext):
    intensity = int(callback.data.replace("diary_int_", ""))
    await state.update_data(intensity=intensity)
    await state.set_state(DiaryFSM.situation)
    await callback.message.edit_text(
        f"Интенсивность: *{intensity}/10*\n\n"
        "Что *произошло* перед этим? Опиши ситуацию кратко.",
        parse_mode="Markdown",
    )
    await callback.answer()


@router.message(DiaryFSM.situation)
async def diary_situation(message: Message, state: FSMContext):
    await state.update_data(situation=message.text.strip())
    await state.set_state(DiaryFSM.thoughts)
    await message.answer(
        "Какие *мысли* пришли вместе с этой эмоцией?\n"
        "_(О себе, других, ситуации?)_",
        parse_mode="Markdown",
    )


@router.message(DiaryFSM.thoughts)
async def diary_thoughts(message: Message, state: FSMContext):
    await state.update_data(thoughts=message.text.strip())
    await state.set_state(DiaryFSM.impulse)
    await message.answer(
        "Что тебе *хотелось сделать* под влиянием этой эмоции?\n"
        "_(Убежать, накричать, закрыться...)_",
        parse_mode="Markdown",
    )


@router.message(DiaryFSM.impulse)
async def diary_impulse(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    add_diary_entry(
        user_id=message.from_user.id,
        emotion=data["emotion"],
        intensity=data["intensity"],
        situation=data["situation"],
        thoughts=data["thoughts"],
        impulse=message.text.strip(),
    )
    await message.answer(
        "✅ *Запись сохранена!*\n\n"
        f"📌 Эмоция: {data['emotion']} ({data['intensity']}/10)\n"
        f"📌 Ситуация: {data['situation']}\n"
        f"📌 Мысли: {data['thoughts']}\n"
        f"📌 Импульс: {message.text.strip()}\n\n"
        "Осознавание — уже первый шаг. Попробуй упражнение в разделе *🧘 Навыки*.",
        parse_mode="Markdown",
        reply_markup=main_kb(),
    )
