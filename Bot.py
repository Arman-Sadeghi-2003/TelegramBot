from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import asyncio

# Replace this with your own bot token from BotFather
BOT_TOKEN = "BOT_TOKEN"

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hi there! I’m your friendly math bot.\n"
        "You can try these commands:\n"
        "/add 3 4\n"
        "/subtract 10 3\n"
        "/multiply 2 5\n"
        "/divide 8 2"
    )

# Add command
async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        x, y = map(float, context.args)
        await update.message.reply_text(f"{x} + {y} = {x + y}")
    except:
        await update.message.reply_text("Usage: /add 3 4")

# Subtract command
async def subtract(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        x, y = map(float, context.args)
        await update.message.reply_text(f"{x} - {y} = {x - y}")
    except:
        await update.message.reply_text("Usage: /subtract 10 3")

# Multiply command
async def multiply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        x, y = map(float, context.args)
        await update.message.reply_text(f"{x} × {y} = {x * y}")
    except:
        await update.message.reply_text("Usage: /multiply 2 5")

# Divide command
async def divide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        x, y = map(float, context.args)
        if y == 0:
            await update.message.reply_text("Cannot divide by zero.")
        else:
            await update.message.reply_text(f"{x} ÷ {y} = {x / y}")
    except:
        await update.message.reply_text("Usage: /divide 8 2")

# Main function to run the bot
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("subtract", subtract))
    app.add_handler(CommandHandler("multiply", multiply))
    app.add_handler(CommandHandler("divide", divide))

    print("Bot is running...")
    await app.run_polling()

# Run the bot
if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(main())
    except RuntimeError as e:
        # fallback for already running loop (like in Railway)
        loop = asyncio.get_event_loop()
        loop.create_task(main())
        loop.run_forever()
