import os
from datetime import datetime
from zoneinfo import ZoneInfo

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

BOT_TOKEN = os.environ["BOT_TOKEN"]
TIMEZONE = ZoneInfo("Asia/Krasnoyarsk")


SHIFT_START = datetime(2026, 9, 10, 13, 0, tzinfo=TIMEZONE)
SHIFT_END = datetime(2026, 10, 12, 7, 0, tzinfo=TIMEZONE)

WEB_APP_URL = os.environ.get(
    "WEB_APP_URL",
    "https://YOUR-USERNAME.github.io/my-shift-app/"
)


def get_shift_info():
    now = datetime.now(TIMEZONE)

    total = (SHIFT_END - SHIFT_START).total_seconds()
    elapsed = (now - SHIFT_START).total_seconds()

    progress = max(0, min(100, elapsed / total * 100))
    remaining = max(0, (SHIFT_END - now).total_seconds())

    return now, progress, remaining


def format_time(seconds):
    seconds = int(seconds)

    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60

    return f"{days} д. {hours} ч. {minutes} мин."


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton(
                "⏳ Открыть таймер",
                web_app=WebAppInfo(url=WEB_APP_URL)
            )
        ],
        [
            InlineKeyboardButton("📊 Моя вахта", callback_data="shift")
        ]
    ]

    await update.message.reply_text(
        "👋 Привет!\n\n"
        "Это твой личный помощник по вахте.\n"
        "Здесь можно посмотреть, сколько осталось до дома 🏠",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def shift(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now, progress, remaining = get_shift_info()

    if remaining <= 0:
        text = (
            "🎉 ТЫ ДОМА!\n\n"
            "Вахта закончена. Можно отдыхать ❤️"
        )
    else:
        text = (
            "⏳ ТВОЯ ВАХТА\n\n"
            f"Осталось: {format_time(remaining)}\n"
            f"Прогресс: {progress:.1f}%\n\n"
            f"Начало: {SHIFT_START.strftime('%d.%m.%Y %H:%M')}\n"
            f"Домой: {SHIFT_END.strftime('%d.%m.%Y %H:%M')}"
        )

    await update.message.reply_text(text)


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("time", shift))

    print("Bot started")

    app.run_polling()


if __name__ == "__main__":
    main()
