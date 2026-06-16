from aiogram import Router, F
from aiogram.types import Message
from utils.keyboards import main_kb

router = Router()

CRISIS_TEXT = (
    "🆘 *Кризисная поддержка*\n\n"
    "Если тебе сейчас очень тяжело — ты не один(а).\n\n"
    "📞 *Телефоны доверия:*\n"
    "• Россия (бесплатно): *8\\-800\\-2000\\-122*\n"
    "• Экстренная помощь: *112*\n"
    "• Международный: befrienders\\.org\n\n"
    "━━━━━━━━━━━━━━━━\n"
    "🧊 *Прямо сейчас — техника TIPP:*\n\n"
    "*1\\. Холодная вода* — умойся ледяной водой 30 секунд\\.\n"
    "*2\\. Движение* — 20 приседаний или отжиманий\\.\n"
    "*3\\. Дыхание 4\\-7\\-8* — вдох 4 сек → задержка 7 → выдох 8\\. Повтори 3 раза\\.\n"
    "*4\\. Расслабление* — напряги всё тело на 5 сек, потом отпусти\\.\n\n"
    "Ты справляешься\\. 💙"
)

CRISIS_KEYWORDS = {
    "хочу умереть", "не хочу жить", "нет смысла",
    "суицид", "убить себя", "конец всему",
    "кризис", "помогите", "не могу больше",
}


def is_crisis(text: str) -> bool:
    t = text.lower()
    return any(kw in t for kw in CRISIS_KEYWORDS)


@router.message(F.text == "🆘 Кризис")
async def show_crisis(message: Message):
    await message.answer(CRISIS_TEXT, parse_mode="MarkdownV2", reply_markup=main_kb())


@router.message(F.text.func(lambda t: t and is_crisis(t)))
async def auto_crisis(message: Message):
    await message.answer(CRISIS_TEXT, parse_mode="MarkdownV2", reply_markup=main_kb())
