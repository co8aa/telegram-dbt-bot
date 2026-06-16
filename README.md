# DBT Telegram Bot

Бот-помощник для практики навыков Диалектической поведенческой терапии (DBT).

## Возможности

- 🧘 **4 модуля навыков DBT** — осознанность, переносимость дистресса, регуляция эмоций, межличностная эффективность
- 🏃 **6 интерактивных упражнений** — 5-4-3-2-1, дыхание 4-7-8, сканирование тела, карточка эмоций, противоположное действие, DEAR MAN
- 📝 **Дневник эмоций** — пошаговая запись через FSM с сохранением в SQLite
- 📊 **Статистика** — последние записи и частые эмоции за неделю
- 🆘 **Кризисная поддержка** — экстренные контакты + техники TIPP, автоматическое определение кризисных фраз

---

## Локальный запуск

```bash
# 1. Клонируй репозиторий / распакуй архив
cd dbt_bot

# 2. Установи зависимости
pip install -r requirements.txt

# 3. Создай файл .env или задай переменную окружения
export BOT_TOKEN="твой_токен_от_BotFather"

# 4. Запусти в режиме polling
python bot.py
```

---

## Деплой на Render (бесплатный план)

### Шаг 1 — Получи токен бота
1. Открой [@BotFather](https://t.me/BotFather) в Telegram
2. Отправь `/newbot`, следуй инструкциям
3. Скопируй токен вида `1234567890:ABCdef...`

### Шаг 2 — Создай репозиторий на GitHub
```bash
git init
git add .
git commit -m "initial"
# создай репо на github.com, затем:
git remote add origin https://github.com/ВАШ_ЛОГИН/dbt-bot.git
git push -u origin main
```

### Шаг 3 — Деплой на Render
1. Зайди на [render.com](https://render.com) → **New → Web Service**
2. Подключи GitHub-репозиторий
3. Настройки:
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python bot.py`
4. Во вкладке **Environment** добавь переменные:
   - `BOT_TOKEN` = твой токен
   - `WEBHOOK_URL` = `https://ИМЯ_СЕРВИСА.onrender.com` *(заполни после деплоя)*
   - `PORT` = `10000`
5. Нажми **Create Web Service**
6. После деплоя скопируй URL из заголовка (например `https://dbt-bot-xxxx.onrender.com`)
7. Вернись в **Environment**, обнови `WEBHOOK_URL` на этот адрес
8. **Manual Deploy → Deploy latest commit**

> ⚠️ На бесплатном плане Render сервис засыпает через 15 минут неактивности.
> Для постоянной работы подключи [UptimeRobot](https://uptimerobot.com) — пинг каждые 5 минут на `/` (бот возвращает 200).

---

## Структура проекта

```
dbt_bot/
├── bot.py              # точка входа, регистрация хэндлеров
├── config.py           # переменные окружения
├── requirements.txt
├── render.yaml         # конфиг Render
├── Procfile
├── data/
│   └── dbt_content.json    # тексты навыков и упражнений
├── handlers/
│   ├── start.py        # /start
│   ├── skills.py       # навыки + упражнения (FSM)
│   ├── diary.py        # дневник эмоций (FSM)
│   ├── crisis.py       # кризисная поддержка
│   └── stats.py        # статистика
├── models/
│   └── user.py         # SQLite: users, diary, skill_log
└── utils/
    └── keyboards.py    # клавиатуры
```

---

## Этические ограничения

- Бот **не является** заменой психотерапевта
- Не хранит личные данные (только `user_id` Telegram)
- При кризисных фразах немедленно показывает телефоны доверия
- Не ставит диагнозов и не интерпретирует состояния
