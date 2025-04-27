from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.ext import MessageHandler, filters, ReplyKeyboardMarkup
import asyncio
import os
import math
from collections import defaultdict

# Replace this with your own bot token from BotFather
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Store command usage statistics
command_stats = defaultdict(int)
FIRST_NUMBER, SECOND_NUMBER = range(2)

# Helper function to validate arguments
def validate_args(args, expected_count):
    if len(args) != expected_count:
        return False, f"Expected {expected_count} number(s)"
    try:
        numbers = [float(arg) for arg in args]
        return True, numbers
    except ValueError:
        return False, "Please provide valid numbers"

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ['/help'],
        ["/add", "/subtract"],
        ["/multiply", "/divide"],
        ["/sin", '/cos', '/tan'],
        ["/square"]
        ["/sqrt", "/pow"],
        ["/log", "/abs", "/round"],
        ["/stats"],
        ["/Cancel"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    command_stats['start'] += 1
    username = update.effective_user.first_name or "there"
    await update.message.reply_text(
        f"👋 Hello {username}! I'm your friendly math assistant.\nAvailable commands:",
        reply_markup=reply_markup
    )
    
# Help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command_stats['help'] += 1
    await update.message.reply_text(
        "📚 MathMasterBot Commands:\n"
        "/start - Welcome message\n"
        "/add x y - Add two numbers\n"
        "/subtract x y - Subtract two numbers\n"
        "/multiply x y - Multiply two numbers\n"
        "/divide x y - Divide two numbers\n"
        "/square x - Square a number\n"
        "/sin x - Calculate sine (in radians)\n"
        "/cos x - Calculate cosine (in radians)\n"
        "/tan x - Calculate tangent (in radians)\n"
        "/sqrt x - Square root\n"
        "/pow x y - x raised to the power y\n"
        "/log x - Natural logarithm (ln)\n"
        "/abs x - Absolute value\n"
        "/round x - Round to nearest integer\n"
        "/stats - Show command usage statistics"
    )

# Add command
async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command_stats['add'] += 1
    is_valid, result = validate_args(context.args, 2)
    if not is_valid:
        await update.message.reply_text(f"Error: {result}\nUsage: /add 3 4")
        return
    x, y = result
    await update.message.reply_text(f"{x} + {y} = {x + y}")

# Subtract command
async def subtract(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command_stats['subtract'] += 1
    is_valid, result = validate_args(context.args, 2)
    if not is_valid:
        await update.message.reply_text(f"Error: {result}\nUsage: /subtract 10 3")
        return
    x, y = result
    await update.message.reply_text(f"{x} - {y} = {x - y}")

# Multiply command
async def multiply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command_stats['multiply'] += 1
    is_valid, result = validate_args(context.args, 2)
    if not is_valid:
        await update.message.reply_text(f"Error: {result}\nUsage: /multiply 2 5")
        return
    x, y = result
    await update.message.reply_text(f"{x} × {y} = {x * y}")

# Divide command
async def divide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command_stats['divide'] += 1
    is_valid, result = validate_args(context.args, 2)
    if not is_valid:
        await update.message.reply_text(f"Error: {result}\nUsage: /divide 8 2")
        return
    x, y = result
    if y == 0:
        await update.message.reply_text("Cannot divide by zero.")
    else:
        await update.message.reply_text(f"{x} ÷ {y} = {x / y}")

# Square command
async def square(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command_stats['square'] += 1
    is_valid, result = validate_args(context.args, 1)
    if not is_valid:
        await update.message.reply_text(f"Error: {result}\nUsage: /square 5")
        return
    x = result[0]
    await update.message.reply_text(f"{x}² = {x * x}")

# Sine command
async def sin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command_stats['sin'] += 1
    is_valid, result = validate_args(context.args, 1)
    if not is_valid:
        await update.message.reply_text(f"Error: {result}\nUsage: /sin 1.57")
        return
    x = result[0]
    await update.message.reply_text(f"sin({x}) = {math.sin(x):.6f}")

# Cosine command
async def cos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command_stats['cos'] += 1
    is_valid, result = validate_args(context.args, 1)
    if not is_valid:
        await update.message.reply_text(f"Error: {result}\nUsage: /cos 1.57")
        return
    x = result[0]
    await update.message.reply_text(f"cos({x}) = {math.cos(x):.6f}")

# Tangent command
async def tan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command_stats['tan'] += 1
    is_valid, result = validate_args(context.args, 1)
    if not is_valid:
        await update.message.reply_text(f"Error: {result}\nUsage: /tan 0.785")
        return
    x = result[0]
    try:
        result = math.tan(x)
        await update.message.reply_text(f"tan({x}) = {result:.6f}")
    except ValueError:
        await update.message.reply_text("Error: Invalid input for tangent")

# Square root command
async def sqrt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command_stats['sqrt'] += 1
    is_valid, result = validate_args(context.args, 1)
    if not is_valid:
        await update.message.reply_text(f"Error: {result}\nUsage: /sqrt 16")
        return
    x = result[0]
    if x < 0:
        await update.message.reply_text("Cannot take square root of a negative number.")
    else:
        await update.message.reply_text(f"√{x} = {math.sqrt(x):.6f}")

# Power command
async def pow_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command_stats['pow'] += 1
    is_valid, result = validate_args(context.args, 2)
    if not is_valid:
        await update.message.reply_text(f"Error: {result}\nUsage: /pow 2 3")
        return
    x, y = result
    await update.message.reply_text(f"{x} ^ {y} = {math.pow(x, y):.6f}")

# Logarithm command
async def log(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command_stats['log'] += 1
    is_valid, result = validate_args(context.args, 1)
    if not is_valid:
        await update.message.reply_text(f"Error: {result}\nUsage: /log 2.718")
        return
    x = result[0]
    if x <= 0:
        await update.message.reply_text("Cannot take log of non-positive number.")
    else:
        await update.message.reply_text(f"ln({x}) = {math.log(x):.6f}")

# Absolute value command
async def abs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command_stats['abs'] += 1
    is_valid, result = validate_args(context.args, 1)
    if not is_valid:
        await update.message.reply_text(f"Error: {result}\nUsage: /abs -5")
        return
    x = result[0]
    await update.message.reply_text(f"|{x}| = {abs(x)}")

# Round command
async def round_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command_stats['round'] += 1
    is_valid, result = validate_args(context.args, 1)
    if not is_valid:
        await update.message.reply_text(f"Error: {result}\nUsage: /round 2.7")
        return
    x = result[0]
    await update.message.reply_text(f"round({x}) = {round(x)}")

# Stats command
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command_stats['stats'] += 1
    stats_message = "📊 Command Usage Statistics:\n"
    for cmd, count in command_stats.items():
        stats_message += f"/{cmd}: {count} times\n"
    await update.message.reply_text(stats_message)


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Unknown command. Try /help to see available commands.")


# Main function to run the bot
def main():
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN not set")
        return

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("subtract", subtract))
    app.add_handler(CommandHandler("multiply", multiply))
    app.add_handler(CommandHandler("divide", divide))
    app.add_handler(CommandHandler("square", square))
    app.add_handler(CommandHandler("sin", sin))
    app.add_handler(CommandHandler("cos", cos))
    app.add_handler(CommandHandler("tan", tan))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("sqrt", sqrt))
    app.add_handler(CommandHandler("pow", pow_command))
    app.add_handler(CommandHandler("log", log))
    app.add_handler(CommandHandler("abs", abs_command))
    app.add_handler(CommandHandler("round", round_command))
    app.add_handler(MessageHandler(filters.COMMAND, unknown_command))

    print("MathMasterBot is running...")
    app.run_polling()

# Run the bot
if __name__ == "__main__":
    main()
