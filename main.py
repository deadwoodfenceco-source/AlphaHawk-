import os
import random

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

TOKEN = os.getenv("TELEGRAM_TOKEN", "").strip()

if not TOKEN:
    raise SystemExit("❌ TELEGRAM_TOKEN is missing")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🦅 AlphaHawk Online!\n\n"
        "Commands:\n"
        "/start\n"
        "/help\n"
        "/test\n"
        "/idea"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Available Commands:\n\n"
        "/start\n"
        "/help\n"
        "/test\n"
        "/idea"
    )


async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ AlphaHawk Test Successful"
    )


async def idea(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ideas = [
        "Build an AI fence estimate generator.",
        "Create a meme coin scanner Telegram bot.",
        "Build a local service lead finder.",
        "Create an AI music video automation system.",
        "Make a crypto news alert bot."
    ]

    await update.message.reply_text(
        random.choice(ideas)
    )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.lower()

    if "hello" in user_text:
        await update.message.reply_text(
            "🦅 Hello Jerren. AlphaHawk standing by."
        )
    else:
        await update.message.reply_text(
            f"🦅 AlphaHawk received:\n\n{update.message.text}"
        )


app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("test", test))
app.add_handler(CommandHandler("idea", idea))

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        echo,
    )
)

app.run_polling()




