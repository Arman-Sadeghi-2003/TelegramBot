from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, Application
from telegram.error import Conflict, TelegramError
import asyncio
import os
import math
from collections import defaultdict
import logging
import sys
import signal

# Try to import pidfile, fallback if not available
try:
    from pidfile import PidFile, PidFileAlreadyRunningError
except ImportError:
    PidFile = None
    PidFileAlreadyRunningError = None
    print("Warning: pidfile module not found. Multiple instances may run concurrently.")

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Replace this with your own bot token from BotFather
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Store command usage statistics
command_stats = defaultdict(int)

# PID file path
PID_FILE = "math_bot.pid"

# Helper function to validate arguments
def validate_args(args, expected_count):
    if len(args) != expected_count:
        return False, f"Expected {expected_count} number(s)"
    try:
        numbers = [float(arg) for arg in args]
        return True, numbers
    except ValueError:
        return False, "Please provide valid numbers"

# Error handler
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error: {context.error}")
    if isinstance(context.error, Conflict):
        logger.error("Conflict error: Another bot instance is running. Terminating...")
        if update:
            await update.message.reply_text(
                "Error: Bot conflict detected. Please ensure only one instance is running."
            )
        sys.exit(1)
    elif update:
        await update.message.reply_text("An error occurred. Please try again later.")

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command_stats['start'] += 1
    await update.message.reply_text(
        "👋 Welcome to MathMasterBot! I'm your friendly math assistant.\n"
        "Available commands:\n"
        "/help - Show all commands\n"
        "/add x y - Add two numbers\n"
        "/subtract x y - Subtract two numbers\n"
        "/multiply x y - Multiply two numbers\n"
        "/divide x y - Divide two numbers\n"
        "/square x - Square a number\n"
        "/sin x - Calculate sine\n"
        "/cos x - Calculate cosine\n"
        "/tan x - Calculate tangent"
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

# Stats command
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command_stats['stats'] += 1
    stats_message = "📊 Command Usage Statistics:\n"
    for cmd, count in command_stats.items():
        stats_message += f"/{cmd}: {count} times\n"
    await update.message.reply_text(stats_message)

# Signal handler for graceful shutdown
def handle_shutdown(signum, frame, application: Application):
    logger.info("Received shutdown signal, stopping bot...")
    asyncio.create_task(application.stop())
    asyncio.create_task(application.shutdown())
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)
    sys.exit(0)

# Main function to run the bot
def main():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN not set")
        return

    # Check for existing instance using PID file
    if PidFile is None:
        logger.warning("pidfile module not available, proceeding without instance checking")
        app = ApplicationBuilder().token(BOT_TOKEN).build()
    else:
        try:
            with PidFile(PID_FILE):
                app = ApplicationBuilder().token(BOT_TOKEN).build()
        except PidFileAlreadyRunningError:
            logger.error("Another instance of MathMasterBot is already running. Exiting...")
            sys.exit(1)

    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, lambda s, f: handle_shutdown(s, f, app))
    signal.signal(signal.SIGTERM, lambda s, f: handle_shutdown(s, f, app))

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

    # Add error handler
    app.add_error_handler(error_handler)

    logger.info("MathMasterBot is running...")
    app.run_polling()

# Run the bot
if __name__ == "__main__":
    main()
