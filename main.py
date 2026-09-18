import os

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# Load token from Railway environment variables
TOKEN = os.getenv("TELEGRAM_TOKEN", "").strip()

if not TOKEN:
    raise SystemExit("❌ TELEGRAM_TOKEN is missing")

print("🦅 AlphaHawk Starting...")
print(f"✅ Token Loaded: {bool(TOKEN)}")


# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🦅 AlphaHawk Online!\n\n"
        "Commands:\n"
        "/start\n"
        "/help\n"
        "/test"
    )


# /help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Available Commands:\n\n"
        "/start - Start AlphaHawk\n"
        "/help - Show commands\n"
        "/test - Test bot"
    )


# /test command
async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ AlphaHawk Test Successful"
    )


# Reply to normal messages
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    await update.message.reply_text(
        f"🦅 You said:\n\n{user_text}"
    )


# Build bot
app = Application.builder().token(TOKEN).build()

# Commands
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("test", test))

# Normal text messages
app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        echo,
    )
)

print("🚀 AlphaHawk Online")

# Start bot
app.run_polling()


