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
        "Commands:\n\n"
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
        "Create an AI fence estimate generator.",
        "Build a meme coin scanner bot.",
        "Create a local lead generation tool.",
        "Build an AI music video pipeline.",
        "Create a crypto alert channel."
    ]

    await update.message.reply_text(
        random.choice(ideas)
    )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.lower()

    responses = [
        "🦅 AlphaHawk received your message.",
        "🦅 Copy that.",
        "🦅 Standing by.",
        "🦅 Message logged.",
        "🦅 AlphaHawk acknowledges."
    ]

    if "hello" in user_text:
        await update.message.reply_text(
            "🦅 Hello Jerren. AlphaHawk standing by."
        )

    elif "btc" in user_text:
        await update.message.reply_text(
           





