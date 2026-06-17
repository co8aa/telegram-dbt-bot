import os
import asyncio
import logging
import sqlite3
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message, CallbackQuery,
    ReplyKeyboardMarkup, KeyboardButton,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN   = os.getenv("BOT_TOKEN", "")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
PORT        = int(os.getenv("PORT", 10000))

# ── Контент встроен прямо в файл ─────────────────────────────────────────────
SKILLS = {
    "mindfulness": {
        "title": "🧘 Осознанность",
        "description": (
            "Осознанность — основа всей DBT. Умение замечать происходящее здесь и сейчас без осуждения.\n\n"
            "Три «что»:\n"
            "• Наблюдение — замечай, не цепляясь\n"
            "• Описание — называй словами то, что видишь\n"
            "• Участие — полностью погружайся в действие\n\n"
            "Три «как»:\n"
            "• Без осуждений — факты, не оценки\n"
            "• Одно дело за раз\n"
            "• Эффективно — делай то, что работает"
        ),
        "exercises": ["ground", "breath", "body"],
    },
    "distress": {
        "title": "🛡 Переносимость дистресса",
        "description": (
            "Навык выживания в острых ситуациях без импульсивных поступков.\n\n"
            "Техники TIPP:\n"
            "• Temperature — холодная вода на лицо\n"
            "• Intense exercise — интенсивная нагрузка\n"
            "• Paced breathing — замедленное дыхание\n"
            "• Progressive relaxation — расслабление мышц\n\n"
            "Отвлечение ACCEPTS:\n"
            "Деятельность, Вклад, Сравнение, Эмоции, Расталкивание, Мысли, Ощущения"
        ),
        "exercises": ["cold", "breath", "ground"],
    },
    "emotion_reg": {
        "title": "🎭 Регуляция эмоций",
        "description": (
            "Умение понимать свои чувства и влиять на них.\n\n"
            "Проверка фактов:\n"
            "Спроси себя: «Мои эмоции соответствуют фактам или я реагирую на интерпретацию?»\n\n"
            "Противоположное действие:\n"
            "• Страх → приближайся\n"
            "• Злость → будь добрым\n"
            "• Грусть → будь активным\n\n"
            "PLEASE — забота о теле:\n"
            "Лечи болезни, сон, питание, избегай алкоголя, физкультура"
        ),
        "exercises": ["opposite", "emotion_card"],
    },
    "interpersonal": {
        "title": "🤝 Межличностная эффективность",
        "description": (
            "Навык общаться так, чтобы добиваться целей и сохранять отношения.\n\n"
            "DEAR MAN — как просить или отказывать:\n"
            "• D — Describe: опиши ситуацию фактами\n"
            "• E — Express: вырази чувства\n"
            "• A — Assert: чётко скажи чего хочешь\n"
            "• R — Reinforce: объясни выгоду\n"
            "• M — Mindful: держи фокус\n"
            "• A — Appear confident: выгляди уверенно\n"
            "• N — Negotiate: будь готов к компромиссу\n\n"
            "GIVE — сохранять отношения:\n"
            "Gentle, Interested, Validate, Easy manner"
        ),
        "exercises": ["dear_man"],
    },
}

EXERCISES = {
    "ground": {
        "title": "🌍 Заземление 5-4-3-2-1",
        "steps": [
            "Назови 5 вещей, которые ты ВИДИШЬ прямо сейчас.",
            "Назови 4 вещи, которые ты СЛЫШИШЬ в данный момент.",
            "Назови 3 вещи, которые ты можешь ПОТРОГАТЬ. Почувствуй их текстуру.",
            "Назови 2 вещи, которые ты чувствуешь на ЗАПАХ.",
            "Назови 1 вещь, которую ты ощущаешь на ВКУС прямо сейчас.\n\n✅ Как ты сейчас? Удалось немного заземлиться?",
        ],
    },
    "breath": {
        "title": "🌬 Дыхание 4-7-8",
        "steps": [
            "Найди удобное положение. Можно закрыть глаза.\n\nДышим по схеме 4-7-8 — это успокоит нервную систему.",
            "Сделай ВДОХ через нос, считая до 4.\n\n1... 2... 3... 4...",
            "ЗАДЕРЖИ дыхание, считая до 7.\n\n1... 2... 3... 4... 5... 6... 7...",
            "ВЫДЫХАЙ через рот, считая до 8.\n\n1... 2... 3... 4... 5... 6... 7... 8...",
            "Повтори ещё 2-3 раза самостоятельно.\n\n✅ Молодец! Как ощущения?",
        ],
    },
    "body": {
        "title": "🔍 Сканирование тела",
        "steps": [
            "Ляг или сядь удобно. Закрой глаза.\n\nПройдёмся вниманием по телу снизу вверх.",
            "Направь внимание на СТОПЫ и пальцы ног.\nЧто ты чувствуешь? Тепло? Напряжение? Просто замечай.",
            "Поднимись вниманием к ГОЛЕНЯМ и коленям.\nЕсть ли там напряжение?",
            "Теперь ЖИВОТ и грудь.\nЗамечай дыхание — грудь поднимается и опускается.",
            "Внимание на ПЛЕЧИ, шею и лицо.\nПозволь мышцам расслабиться.\n\n✅ Упражнение завершено. Как ты сейчас?",
        ],
    },
    "cold": {
        "title": "🧊 Холодная вода",
        "steps": [
            "Техника TIPP — температура.\n\nПодойди к раковине или возьми стакан холодной воды.",
            "Умойся ледяной водой или подержи запястья под холодной струёй 30 секунд.",
            "Почувствуй как тело реагирует — это активирует парасимпатическую нервную систему.",
            "Сделай медленный выдох.\n\n✅ Как ощущения? Немного легче?",
        ],
    },
    "opposite": {
        "title": "🔄 Противоположное действие",
        "steps": [
            "Противоположное действие работает когда эмоция не соответствует фактам.\n\nКакую эмоцию ты хочешь изменить? Просто прочитай и подумай.",
            "Что эта эмоция подталкивает тебя сделать?\nНапример: страх → избегать, злость → атаковать, грусть → закрыться.",
            "Спроси себя: соответствует ли эта эмоция реальным фактам?\nИли ты реагируешь на интерпретацию?",
            "Попробуй сделать ПРОТИВОПОЛОЖНОЕ:\n• Страх → сделай один шаг навстречу\n• Грусть → встань и подвигайся\n• Злость → сделай что-то доброе",
            "✅ Помни: нужно делать это полностью и неоднократно — тогда эмоция начнёт меняться.",
        ],
    },
    "emotion_card": {
        "title": "📋 Карточка эмоций",
        "steps": [
            "Заполним карточку эмоции — это помогает лучше понять что происходит.\n\nПросто читай и отвечай себе мысленно или вслух.",
            "Что произошло перед тем как ты почувствовал(а) эту эмоцию?\nОпиши ситуацию фактами.",
            "Какие мысли пришли вместе с эмоцией?\nЧто ты подумал(а) о себе, других, ситуации?",
            "Что тебе хотелось сделать под влиянием этой эмоции?\nУбежать? Накричать? Закрыться?",
            "✅ Осознавание — уже первый шаг к изменениям.\nЕсли хочешь записать — используй раздел Дневник.",
        ],
    },
    "dear_man": {
        "title": "💬 DEAR MAN",
        "steps": [
            "DEAR MAN помогает попросить о чём-то или отказать, сохраняя отношения.\n\nПодумай о ситуации в которой тебе нужно это применить.",
            "D — Describe (Опиши)\nОпиши ситуацию фактами без оценок.\nПример: «В последние две недели когда я прошу помочь...»",
            "E — Express (Вырази)\nВырази чувства через Я-высказывания.\nПример: «Я чувствую усталость и одиночество...»",
            "A — Assert (Скажи чётко)\nЧётко скажи чего хочешь.\nПример: «Мне нужно чтобы ты выделял 30 минут раз в неделю...»",
            "R — Reinforce (Объясни выгоду)\nПокажи почему это важно для обоих.\n\n✅ Потренируй этот разговор перед зеркалом. Ты справишься!",
        ],
    },
}

# ── База данных ───────────────────────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect("dbt_bot.db")
    conn.execute("""CREATE TABLE IF NOT EXISTS diary (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER, emotion TEXT, intensity INTEGER,
        situation TEXT, thoughts TEXT, impulse TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)""")
    conn.commit()
    conn.close()

def save_diary(user_id, emotion, intensity, situation, thoughts, impulse):
    conn = sqlite3.connect("dbt_bot.db")
    conn.execute(
        "INSERT INTO diary (user_id,emotion,intensity,situation,thoughts,impulse) VALUES (?,?,?,?,?,?)",
        (user_id, emotion, intensity, situation, thoughts, impulse))
    conn.commit()
    conn.close()

def get_diary(user_id, limit=5):
    conn = sqlite3.connect("dbt_bot.db")
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT emotion,intensity,situation,timestamp FROM diary WHERE user_id=? ORDER BY timestamp DESC LIMIT ?",
        (user_id, limit)).fetchall()
    conn.close()
    return rows

# ── Клавиатуры ────────────────────────────────────────────────────────────────
def main_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🧘 Навыки"),  KeyboardButton(text="📝 Дневник")],
            [KeyboardButton(text="🆘 Кризис"),  KeyboardButton(text="📊 Статистика")],
        ],
        resize_keyboard=True,
    )

def skills_kb():
    b = InlineKeyboardBuilder()
    for key, val in SKILLS.items():
        b.button(text=val["title"], callback_data=f"skill_{key}")
    b.adjust(1)
    return b.as_markup()

def exercises_kb(ex_keys):
    b = InlineKeyboardBuilder()
    for key in ex_keys:
        ex = EXERCISES.get(key)
        if ex:
            b.button(text=ex["title"], callback_data=f"ex_{key}|0")
    b.button(text="◀️ Назад к навыкам", callback_data="back_skills")
    b.adjust(1)
    return b.as_markup()

def next_btn(ex_key, step):
    b = InlineKeyboardBuilder()
    b.button(text="➡️ Далее", callback_data=f"ex_{ex_key}|{step}")
    return b.as_markup()

def done_btn():
    b = InlineKeyboardBuilder()
    b.button(text="🏠 Главное меню", callback_data="main_menu")
    return b.as_markup()

def intensity_kb():
    b = InlineKeyboardBuilder()
    for i in range(0, 11):
        b.button(text=str(i), callback_data=f"di_{i}")
    b.adjust(6, 5)
    return b.as_markup()

# ── FSM дневника ──────────────────────────────────────────────────────────────
class Diary(StatesGroup):
    emotion   = State()
    intensity = State()
    situation = State()
    thoughts  = State()
    impulse   = State()

# ── Диспетчер ─────────────────────────────────────────────────────────────────
dp = Dispatcher(storage=MemoryStorage())

@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Привет! 👋\n\n"
        "Я помогу практиковать навыки DBT.\n\n"
        "⚠️ Бот — дополнение к терапии, не её замена.\n\n"
        "Выбери раздел 👇",
        reply_markup=main_kb(),
    )

@dp.message(F.text == "🧘 Навыки")
async def show_skills(message: Message):
    await message.answer("📚 Навыки DBT\n\nВыбери модуль:", reply_markup=skills_kb())

@dp.callback_query(F.data.startswith("skill_"))
async def skill_detail(cb: CallbackQuery):
    key   = cb.data.replace("skill_", "")
    skill = SKILLS.get(key)
    if not skill:
        return await cb.answer("Не найдено")
    await cb.message.edit_text(
        f"{skill['title']}\n\n{skill['description']}",
        reply_markup=exercises_kb(skill["exercises"]),
    )
    await cb.answer()

@dp.callback_query(F.data == "back_skills")
async def back_skills(cb: CallbackQuery):
    await cb.message.edit_text("📚 Навыки DBT\n\nВыбери модуль:", reply_markup=skills_kb())
    await cb.answer()

@dp.callback_query(F.data.startswith("ex_"))
async def exercise_step(cb: CallbackQuery):
    parts = cb.data[3:].rsplit("|", 1)
    key  = parts[0]
    step = int(parts[1])
    exercise = EXERCISES.get(key)
    if not exercise:
        return await cb.answer("Не найдено")
    steps = exercise["steps"]
    text  = f"{exercise['title']}\n\nШаг {step+1} из {len(steps)}:\n\n{steps[step]}"
    kb    = next_btn(key, step + 1) if step + 1 < len(steps) else done_btn()
    await cb.message.edit_text(text, reply_markup=kb)
    await cb.answer()

@dp.callback_query(F.data == "main_menu")
async def to_main(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.delete()
    await cb.message.answer("Выбери раздел 👇", reply_markup=main_kb())
    await cb.answer()

@dp.message(F.text == "📝 Дневник")
async def diary_start(message: Message, state: FSMContext):
    await state.set_state(Diary.emotion)
    await message.answer(
        "📝 Дневник эмоций\n\n"
        "Я задам несколько вопросов — займёт около минуты.\n\n"
        "Какую эмоцию ты сейчас чувствуешь? Напиши одним словом.\n"
        "(тревога, злость, грусть, страх...)"
    )

@dp.message(Diary.emotion)
async def diary_emotion(message: Message, state: FSMContext):
    await state.update_data(emotion=message.text.strip())
    await state.set_state(Diary.intensity)
    await message.answer(
        f"Эмоция: {message.text.strip()}\n\nОцени интенсивность от 0 до 10:",
        reply_markup=intensity_kb(),
    )

@dp.callback_query(F.data.startswith("di_"), Diary.intensity)
async def diary_intensity(cb: CallbackQuery, state: FSMContext):
    intensity = int(cb.data.replace("di_", ""))
    await state.update_data(intensity=intensity)
    await state.set_state(Diary.situation)
    await cb.message.edit_text(f"Интенсивность: {intensity}/10\n\nЧто произошло перед этим? Опиши кратко.")
    await cb.answer()

@dp.message(Diary.situation)
async def diary_situation(message: Message, state: FSMContext):
    await state.update_data(situation=message.text.strip())
    await state.set_state(Diary.thoughts)
    await message.answer("Какие мысли пришли вместе с этой эмоцией?")

@dp.message(Diary.thoughts)
async def diary_thoughts(message: Message, state: FSMContext):
    await state.update_data(thoughts=message.text.strip())
    await state.set_state(Diary.impulse)
    await message.answer("Что хотелось сделать под влиянием этой эмоции?\n(убежать, накричать, закрыться...)")

@dp.message(Diary.impulse)
async def diary_impulse(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    save_diary(message.from_user.id, data["emotion"], data["intensity"],
               data["situation"], data["thoughts"], message.text.strip())
    await message.answer(
        "✅ Запись сохранена!\n\n"
        f"Эмоция: {data['emotion']} ({data['intensity']}/10)\n"
        f"Ситуация: {data['situation']}\n"
        f"Мысли: {data['thoughts']}\n"
        f"Импульс: {message.text.strip()}",
        reply_markup=main_kb(),
    )

@dp.message(F.text == "🆘 Кризис")
async def crisis(message: Message):
    await message.answer(
        "🆘 Кризисная поддержка\n\n"
        "Если тебе сейчас очень тяжело — ты не один(а).\n\n"
        "📞 Телефоны доверия:\n"
        "• Россия (бесплатно): 8-800-2000-122\n"
        "• Экстренная помощь: 112\n\n"
        "Прямо сейчас попробуй:\n"
        "1. Холодная вода — умойся ледяной водой 30 секунд\n"
        "2. Движение — 20 приседаний\n"
        "3. Дыхание — вдох 4 сек, задержка 7, выдох 8. Повтори 3 раза\n\n"
        "Ты справляешься 💙",
        reply_markup=main_kb(),
    )

@dp.message(F.text == "📊 Статистика")
async def stats(message: Message):
    rows = get_diary(message.from_user.id)
    if not rows:
        return await message.answer(
            "Записей пока нет.\nНачни с раздела 📝 Дневник",
            reply_markup=main_kb(),
        )
    lines = ["📊 Последние записи:\n"]
    for r in rows:
        lines.append(f"• {r['timestamp'][:10]} — {r['emotion']} ({r['intensity']}/10): {r['situation']}")
    await message.answer("\n".join(lines), reply_markup=main_kb())

@dp.message()
async def fallback(message: Message):
    await message.answer("Воспользуйся кнопками меню или нажми /start 👇", reply_markup=main_kb())

# ── Запуск ────────────────────────────────────────────────────────────────────
async def main():
    init_db()
    bot = Bot(token=BOT_TOKEN)
    if WEBHOOK_URL:
        wh = f"{WEBHOOK_URL}/webhook/{BOT_TOKEN}"
        await bot.set_webhook(wh)
        logger.info(f"Webhook: {wh}")
        app = web.Application()
        SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=f"/webhook/{BOT_TOKEN}")
        setup_application(app, dp, bot=bot)
        runner = web.AppRunner(app)
        await runner.setup()
        await web.TCPSite(runner, "0.0.0.0", PORT).start()
        await asyncio.Event().wait()
    else:
        await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
