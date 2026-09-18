import json
import os
from pathlib import Path
from urllib.parse import quote

import httpx
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
DEXSCREENER_SEARCH_URL = (
    "https://api.dexscreener.com/latest/dex/search?q="
)

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


def save_watchlist(items):
    with WATCHLIST_FILE.open("w", encoding="utf-8") as file:
        json.dump(items, file, indent=2)


watchlist = load_watchlist()


# ==========================================
# FORMATTING
# ==========================================

def format_money(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "Unavailable"

    if number >= 1_000_000_000:
        return f"${number / 1_000_000_000:,.2f}B"

    if number >= 1_000_000:
        return f"${number / 1_000_000:,.2f}M"

    if number >= 1_000:
        return f"${number / 1_000:,.2f}K"

    return f"${number:,.2f}"


def format_price(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "Unavailable"

    if number >= 1:
        return f"${number:,.6f}"

    if number >= 0.01:
        return f"${number:.8f}"

    return f"${number:.12f}".rstrip("0")


def format_percentage(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "Unavailable"

    symbol = "+" if number > 0 else ""
    return f"{symbol}{number:.2f}%"


# ==========================================
# DEXSCREENER LOOKUP
# ==========================================

async def fetch_best_pair(search_term):
    encoded_term = quote(search_term.strip())
    url = f"{DEXSCREENER_SEARCH_URL}{encoded_term}"

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()

    pairs = data.get("pairs") or []

    if not pairs:
        return None

    requested = search_term.upper().strip()

    exact_matches = []

    for pair in pairs:
        base_token = pair.get("baseToken") or {}
        base_symbol = str(base_token.get("symbol", "")).upper()

        if base_symbol == requested:
            exact_matches.append(pair)

    candidates = exact_matches if exact_matches else pairs

    def liquidity_value(pair):
        liquidity = pair.get("liquidity") or {}

        try:
            return float(liquidity.get("usd") or 0)
        except (TypeError, ValueError):
            return 0

    return max(candidates, key=liquidity_value)


def build_pair_message(pair):
    base_token = pair.get("baseToken") or {}
    quote_token = pair.get("quoteToken") or {}
    liquidity = pair.get("liquidity") or {}
    volume = pair.get("volume") or {}
    changes = pair.get("priceChange") or {}

    symbol = base_token.get("symbol", "Unknown")
    name = base_token.get("name", "Unknown")
    quote_symbol = quote_token.get("symbol", "Unknown")
    chain = pair.get("chainId", "Unknown")
    dex = pair.get("dexId", "Unknown")
    price = format_price(pair.get("priceUsd"))
    liquidity_usd = format_money(liquidity.get("usd"))
    volume_24h = format_money(volume.get("h24"))
    change_1h = format_percentage(changes.get("h1"))
    change_24h = format_percentage(changes.get("h24"))
    market_cap = format_money(
        pair.get("marketCap") or pair.get("fdv")
    )
    pair_url = pair.get("url", "Unavailable")
    contract = base_token.get("address", "Unavailable")

    return (
        f"🦅 {name} ({symbol})\n\n"
        f"Price: {price}\n"
        f"1-hour change: {change_1h}\n"
        f"24-hour change: {change_24h}\n"
        f"24-hour volume: {volume_24h}\n"
        f"Liquidity: {liquidity_usd}\n"
        f"Market cap/FDV: {market_cap}\n\n"
        f"Chain: {chain}\n"
        f"DEX: {dex}\n"
        f"Pair: {symbol}/{quote_symbol}\n\n"
        f"Contract:\n{contract}\n\n"
        f"Chart:\n{pair_url}\n\n"
        "⚠️ Verify the contract address before trading."
    )


# ==========================================
# /start
# ==========================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "🦅 AlphaHawk Meme Monitor V3 Online!\n\n"
        "Commands:\n\n"
        "/price PEPE - Get a live price\n"
        "/watch PEPE - Add a coin\n"
        "/unwatch PEPE - Remove a coin\n"
        "/watchlist - Show watched coins\n"
        "/scan - Scan the entire watchlist\n"
        "/status - Show bot status\n"
        "/clearwatchlist - Remove all coins\n"
        "/help - Show instructions\n"
        "/test - Test AlphaHawk"
    )


# ==========================================
# /help
# ==========================================

async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "🦅 AlphaHawk Instructions\n\n"
        "Check one live price:\n"
        "/price PEPE\n\n"
        "For better accuracy, use a contract address:\n"
        "/price CONTRACT_ADDRESS\n\n"
        "Add a coin:\n"
        "/watch PEPE\n\n"
        "Remove a coin:\n"
        "/unwatch PEPE\n\n"
        "Show monitored coins:\n"
        "/watchlist\n\n"
        "Get live data for every watched coin:\n"
        "/scan\n\n"
        "Check bot status:\n"
        "/status"
    )


# ==========================================
# /test
# ==========================================

async def test(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "✅ AlphaHawk Version 3 is working."
    )


# ==========================================
# /price
# ==========================================

async def price(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not context.args:
        await update.message.reply_text(
            "Enter a symbol or contract address.\n\n"
            "Examples:\n"
            "/price PEPE\n"
            "/price CONTRACT_ADDRESS"
        )
        return

    search_term = " ".join(context.args).strip()

    await update.message.reply_text(
        f"🔍 Searching for {search_term}..."
    )

    try:
        pair = await fetch_best_pair(search_term)

        if not pair:
            await update.message.reply_text(
                f"❌ No trading pair found for {search_term}."
            )
            return

        await update.message.reply_text(
            build_pair_message(pair),
            disable_web_page_preview=True
        )

    except httpx.TimeoutException:
        await update.message.reply_text(
            "❌ Price lookup timed out. Try again."
        )

    except httpx.HTTPError as error:
        print(f"Price lookup HTTP error: {error}")

        await update.message.reply_text(
            "❌ The market-data service could not be reached."
        )

    except Exception as error:
        print(f"Price lookup error: {error}")

        await update.message.reply_text(
            "❌ AlphaHawk could not process that price."
        )


# ==========================================
# /watch
# ==========================================

async def watch(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not context.args:
        await update.message.reply_text(
            "Enter a symbol after /watch.\n\n"
            "Example:\n"
            "/watch PEPE"
        )
        return

    symbol = context.args[0].upper().strip()

    if not symbol.isalnum():
        await update.message.reply_text(
            "❌ Use only letters and numbers for watchlist symbols."
        )
        return

    if len(symbol) > 20:
        await update.message.reply_text(
            "❌ That symbol is too long."
        )
        return

    if symbol in watchlist:
        await update.message.reply_text(
            f"⚠️ {symbol} is already on the watchlist."
        )
        return

    watchlist.append(symbol)
    watchlist.sort()
    save_watchlist(watchlist)

    await update.message.reply_text(
        f"✅ {symbol} added.\n\n"
        f"Coins monitored: {len(watchlist)}"
    )


# ==========================================
# /unwatch
# ==========================================

async def unwatch(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not context.args:
        await update.message.reply_text(
            "Enter a symbol after /unwatch.\n\n"
            "Example:\n"
            "/unwatch PEPE"
        )
        return

    symbol = context.args[0].upper().strip()

    if symbol not in watchlist:
        await update.message.reply_text(
            f"⚠️ {symbol} is not on the watchlist."
        )
        return

    watchlist.remove(symbol)
    save_watchlist(watchlist)

    await update.message.reply_text(
        f"✅ {symbol} removed.\n\n"
        f"Coins monitored: {len(watchlist)}"
    )


# ==========================================
# /watchlist
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

    lines = [
        f"{number}. {symbol}"
        for number, symbol in enumerate(watchlist, start=1)
    ]

    await update.message.reply_text(
        "🦅 AlphaHawk Watchlist\n\n"
        + "\n".join(lines)
        + f"\n\nTotal: {len(watchlist)}"
    )


# ==========================================
# /scan
# ==========================================

async def scan(
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

    await update.message.reply_text(
        f"🔍 Scanning {len(watchlist)} coin(s)..."
    )

    results = []

    for symbol in watchlist:
        try:
            pair = await fetch_best_pair(symbol)

            if not pair:
                results.append(
                    f"{symbol}: No pair found"
                )
                continue

            changes = pair.get("priceChange") or {}
            price_usd = format_price(pair.get("priceUsd"))
            change_24h = format_percentage(
                changes.get("h24")
            )
            chain = pair.get("chainId", "Unknown")

            results.append(
                f"{symbol}\n"
                f"Price: {price_usd}\n"
                f"24h: {change_24h}\n"
                f"Chain: {chain}"
            )

        except Exception as error:
            print(f"Scan error for {symbol}: {error}")
            results.append(
                f"{symbol}: Lookup failed"
            )

    await update.message.reply_text(
        "🦅 AlphaHawk Scan\n\n"
        + "\n\n".join(results)
        + "\n\n⚠️ Verify contract addresses before trading."
    )


# ==========================================
# /status
# ==========================================

async def status(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "🦅 AlphaHawk Status\n\n"
        "Bot: Online ✅\n"
        "Live price lookup: Online ✅\n"
        "Watchlist scanner: Online ✅\n"
        f"Coins monitored: {len(watchlist)}\n"
        "Automatic alerts: Not added yet"
    )


# ==========================================
# /clearwatchlist
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
# NORMAL TEXT
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

    else:
        await update.message.reply_text(
            "🦅 Command not recognized.\n\n"
            "Type /help to see all commands."
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
# BUILD AND START
# ==========================================

app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("test", test))
app.add_handler(CommandHandler("price", price))
app.add_handler(CommandHandler("watch", watch))
app.add_handler(CommandHandler("unwatch", unwatch))
app.add_handler(CommandHandler("watchlist", show_watchlist))
app.add_handler(CommandHandler("scan", scan))
app.add_handler(CommandHandler("status", status))
app.add_handler(
    CommandHandler("clearwatchlist", clear_watchlist)
)

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        echo
    )
)

app.add_error_handler(error_handler)

print("🦅 AlphaHawk Version 3 starting...")
print(f"Watchlist loaded: {len(watchlist)} coins")

app.run_polling()


           





