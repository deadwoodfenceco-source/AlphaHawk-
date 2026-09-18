imasync def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🦅 AlphaHawk Online\n\n"
        "Commands:\n"
        "/start\n"
        "/test\n"
        "/help"
    )

async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Test successful")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Available Commands:\n\n"
        "/start\n"
        "/test\n"
        "/help"
        app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("test", test))
app.add_handler(CommandHandler("help", help_command))

    )


app 
print("🦅 AlphaHawk polling started")

app.run_polling()

