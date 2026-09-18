import json
import os
from pathlib import Path

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)


# ==========================================
# CONFIGURATION
# ==========================================

TOKEN = os.getenv("TELEGRAM_TOKEN", "").strip()
WATCHLIST_FILE = Path("watchlist.json")

if not TOKEN:
    raise SystemExit("TELEGRAM_TOKEN is missing")


# ==========================================
# WATCHLIST STORAGE
# ==========================================

def load_watchlist():
    if not WATCHLIST_FILE.exists():
        return []

    try:
        with WATCHLIST_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

    except (json.JSONDecodeError, OSError):
        pass

    return []


def save_watchlist(watchlist):
    with WATCHLIST_FILE.open("w", encoding="utf-8") as file:
        json.dump(watchlist, file, indent=2)


watchlist = load_watchlist()


# ==========================================
# /start COMMAND
# ==========================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    message = (
        "🦅 AlphaHawk Meme Monitor Online!\n\n"
        "Available commands:\n\n"
        "/watch PEPE - Add a coin\n"
        "/unwatch PEPE - Remove a coin\n"
        "/watchlist - Show monitored coins\n"
        "/status - Show monitor status\n"
        "/clearwatchlist - Remove all coins\n"
        "/help - Show instructions\n"
        "/test - Test the bot"
    )

    await update.message.reply_text(message)


# ==========================================
# /help COMMAND
# ==========================================

async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    message = (
        "🦅 AlphaHawk Instructions\n\n"
        "Add a meme coin:\n"
        "/watch PEPE\n\n"
        "Remove a meme coin:\n"
        "/unwatch PEPE\n\n"
        "See your watchlist:\n"
        "/watchlist\n\n"
        "Check AlphaHawk status:\n"
        "/status\n\n"
        "Delete the entire watchlist:\n"
        "/clearwatchlist\n\n"
        "Test the bot:\n"
        "/test"
    )

    await update.message.reply_text(message)


# ==========================================
# /test COMMAND
# ==========================================

async def test(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "✅ AlphaHawk Version 2 is working."
    )


# ==========================================
# /watch COMMAND
# ==========================================

async def watch(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not context.args:
        await update.message.reply_text(
            "Enter a coin symbol after /watch.\n\n"
            "Example:\n"
            "/watch PEPE"
        )
        return

    symbol = context.args[0].upper().strip()

    if not symbol.isalnum():
        await update.message.reply_text(
            "❌ Use only letters and numbers.\n\n"
            "Example:\n"
            "/watch PEPE"
        )
        return

    if len(symbol) > 20:
        await update.message.reply_text(
            "❌ That symbol is too long."
        )
        return

    if symbol in watchlist:
        await update.message.reply_text(
            f"⚠️ {symbol} is already on your watchlist."
        )
        return

    watchlist.append(symbol)
    watchlist.sort()
    save_watchlist(watchlist)

    await update.message.reply_text(
        f"✅ {symbol} added to the watchlist.\n\n"
        f"Total coins monitored: {len(watchlist)}"
    )


# ==========================================
# /unwatch COMMAND
# ==========================================

async def unwatch(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not context.args:
        await update.message.reply_text(
            "Enter a coin symbol after /unwatch.\n\n"
            "Example:\n"
            "/unwatch PEPE"
        )
        return

    symbol = context.args[0].upper().strip()

    if symbol not in watchlist:
        await update.message.reply_text(
            f"⚠️ {symbol} is not on your watchlist."
        )
        return

    watchlist.remove(symbol)
    save_watchlist(watchlist)

    await update.message.reply_text(
        f"✅ {symbol} removed from the watchlist.\n\n"
        f"Total coins monitored: {len(watchlist)}"
    )


# ==========================================
# /watchlist COMMAND
# ==========================================

async def show_watchlist(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not watchlist:
        await update.message.reply_text(
            "🦅 Your watchlist is empty.\n\n"
            "Add a coin with:\n"
            "/watch PEPE"
        )
        return

    coin_lines = []

    for number, symbol in enumerate(watchlist, start=1):
        coin_lines.append(f"{number}. {symbol}")

    formatted_watchlist = "\n".join(coin_lines)

    await update.message.reply_text(
        "🦅 AlphaHawk Watchlist\n\n"
        f"{formatted_watchlist}\n\n"
        f"Total: {len(watchlist)}"
    )


# ==========================================
# /status COMMAND
# ==========================================

async def status(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "🦅 AlphaHawk Status\n\n"
        "Bot: Online ✅\n"
        "Meme monitor: Ready ✅\n"
        f"Coins on watchlist: {len(watchlist)}\n"
        "Live price scanning: Not added yet\n"
        "Automatic alerts: Not added yet"
    )


# ==========================================
# /clearwatchlist COMMAND
# ==========================================

async def clear_watchlist(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    watchlist.clear()
    save_watchlist(watchlist)

    await update.message.reply_text(
        "✅ The entire watchlist has been cleared."
    )


# ==========================================
# NORMAL TEXT REPLIES
# ==========================================

async def echo(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    user_text = update.message.text.strip()
    lowercase_text = user_text.lower()

    if lowercase_text in {"hello", "hi", "hey"}:
        await update.message.reply_text(
            "🦅 Hello Jerren. AlphaHawk is standing by."
        )

    elif "watchlist" in lowercase_text:
        await update.message.reply_text(
            "Use /watchlist to see your monitored coins."
        )

    elif "status" in lowercase_text:
        await update.message.reply_text(
            "Use /status to check AlphaHawk."
        )

    elif "watch" in lowercase_text:
        await update.message.reply_text(
            "To add a coin, type:\n"
            "/watch PEPE"
        )

    else:
        await update.message.reply_text(
            "🦅 Command not recognized.\n\n"
            "Type /help to see available commands."
        )


# ==========================================
# ERROR HANDLER
# ==========================================

async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE
):
    print(f"AlphaHawk error: {context.error}")


# ==========================================
# BUILD APPLICATION
# ==========================================

app = Application.builder().token(TOKEN).build()


# ==========================================
# REGISTER COMMANDS
# ==========================================

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("test", test))
app.add_handler(CommandHandler("watch", watch))
app.add_handler(CommandHandler("unwatch", unwatch))
app.add_handler(CommandHandler("watchlist", show_watchlist))
app.add_handler(CommandHandler("status", status))
app.add_handler(
    CommandHandler("clearwatchlist", clear_watchlist)
)


# ==========================================
# REGISTER NORMAL MESSAGES
# ==========================================

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        echo
    )
)

app.add_error_handler(error_handler)


# ==========================================
# START ALPHAHAWK
# ==========================================

print("🦅 AlphaHawk Version 2 starting...")
print(f"Watchlist loaded: {len(watchlist)} coins")

app.run_polling()


           





