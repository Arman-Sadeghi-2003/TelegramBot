import asyncio
import os
import math
from collections import defaultdict
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

# Replace this with your own bot token from BotFather
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Store command usage statistics
command_stats = defaultdict(int)

# States for conversation handlers
FIRST_NUMBER, SECOND_NUMBER = range(2)

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("/help", callback_data='help_command')],
        [InlineKeyboardButton("/add", callback_data='add'), InlineKeyboardButton("/subtract", callback_data='subtract')],
        [InlineKeyboardButton("/multiply", callback_data='multiply'), InlineKeyboardButton("/divide", callback_data='divide')],
        [InlineKeyboardButton("/sin", callback_data='sin'), InlineKeyboardButton("/cos", callback_data='cos'), InlineKeyboardButton("/tan", callback_data='tan')],
        [InlineKeyboardButton("/square", callback_data='square')],
        [InlineKeyboardButton("/sqrt", callback_data='sqrt'), InlineKeyboardButton("/pow", callback_data='pow')],
        [InlineKeyboardButton("/log", callback_data='log'), InlineKeyboardButton("/abs", callback_data='abs'), InlineKeyboardButton("/round", callback_data='round')],
        [InlineKeyboardButton("/stats", callback_data='stats')],
        [InlineKeyboardButton("/Cancel", callback_data='cancel')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    command_stats['start'] += 1
    username = update.effective_user.first_name or "there"
    message = f"👋 Hello {username}! I'm your friendly math assistant.\nAvailable commands:"
    if update.callback_query:
        await update.callback_query.message.reply_text(message, reply_markup=reply_markup)
        await update.callback_query.answer()
    else:
        await update.message.reply_text(message, reply_markup=reply_markup)

# Help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command_stats['help'] += 1
    help_text = (
        "📚 MathMasterBot Commands:\n"
        "/start - Welcome message\n"
        "/add - Add two numbers\n"
        "/subtract - Subtract two numbers\n"
        "/multiply - Multiply two numbers\n"
        "/divide - Divide two numbers\n"
        "/square - Square a number\n"
        "/sin - Calculate sine (in radians)\n"
        "/cos - Calculate cosine (in radians)\n"
        "/tan - Calculate tangent (in radians)\n"
        "/sqrt - Square root\n"
        "/pow - x raised to the power y\n"
        "/log - Natural logarithm (ln)\n"
        "/abs - Absolute value\n"
        "/round - Round to nearest integer\n"
        "/stats - Show command usage statistics\n"
        "/cancel - Cancel the current operation"
    )
    if update.callback_query:
        await update.callback_query.message.reply_text(help_text)
        await update.callback_query.answer()
    else:
        await update.message.reply_text(help_text)

# Stats command
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command_stats['stats'] += 1
    stats_message = "📊 Command Usage Statistics:\n"
    for cmd, count in command_stats.items():
        stats_message += f"/{cmd}: {count} times\n"
    if update.callback_query:
        await update.callback_query.message.reply_text(stats_message)
        await update.callback_query.answer()
    else:
        await update.message.reply_text(stats_message)

# Cancel command
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command_stats['cancel'] += 1
    cancellation_message = "Operation canceled."
    if update.callback_query:
        await update.callback_query.message.reply_text(cancellation_message)
        await update.callback_query.answer()
    else:
        await update.message.reply_text(cancellation_message)
    return ConversationHandler.END

# Generic function to handle one number operations
async def one_number_entry(update: Update, context: ContextTypes.DEFAULT_TYPE, command: str):
    command_stats[command] += 1
    context.user_data['command'] = command
    message = "Please enter a number:"
    if update.callback_query:
        await update.callback_query.message.reply_text(message)
        await update.callback_query.answer()
    else:
        await update.message.reply_text(message)
    return FIRST_NUMBER

async def one_number_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        number = float(update.message.text)
        command = context.user_data.get('command')
        result = handle_one_number_operation(command, number)
        await update.message.reply_text(result)
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("Please enter a valid number.")
        return FIRST_NUMBER

# Perform the operation based on the command
def handle_one_number_operation(command: str, number: float) -> str:
    if command == 'square':
        return f"{number}² = {number * number}"
    elif command == 'sin':
        return f"sin({number}) = {math.sin(number):.6f}"
    elif command == 'cos':
        return f"cos({number}) = {math.cos(number):.6f}"
    elif command == 'tan':
        try:
            result = math.tan(number)
            return f"tan({number}) = {result:.6f}"
        except ValueError:
            return "Error: Invalid input for tangent"
    elif command == 'sqrt':
        if number < 0:
            return "Cannot take square root of a negative number."
        return f"√{number} = {math.sqrt(number):.6f}"
    elif command == 'log':
        if number <= 0:
            return "Cannot take log of non-positive number."
        return f"ln({number}) = {math.log(number):.6f}"
    elif command == 'abs':
        return f"|{number}| = {abs(number)}"
    elif command == 'round':
        return f"round({number}) = {round(number)}"
    return "Unknown command."

# Generic function to handle two number operations
async def two_number_entry(update: Update, context: ContextTypes.DEFAULT_TYPE, command: str):
    command_stats[command] += 1
    context.user_data['command'] = command
    message = "Please enter the first number:"
    if update.callback_query:
        await update.callback_query.message.reply_text(message)
        await update.callback_query.answer()
    else:
        await update.message.reply_text(message)
    return FIRST_NUMBER

async def first_number_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data['first_number'] = float(update.message.text)
        await update.message.reply_text("Please enter the second number:")
        return SECOND_NUMBER
    except ValueError:
        await update.message.reply_text("Please enter a valid number.")
        return FIRST_NUMBER

async def second_number_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        second_number = float(update.message.text)
        first_number = context.user_data.get('first_number')
        command = context.user_data.get('command')
        result = handle_two_number_operation(command, first_number, second_number)
        await update.message.reply_text(result)
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("Please enter a valid number.")
        return SECOND_NUMBER

# Perform the operation based on the command
def handle_two_number_operation(command: str, first_number: float, second_number: float) -> str:
    if command == 'add':
        return f"{first_number} + {second_number} = {first_number + second_number}"
    elif command == 'subtract':
        return f"{first_number} - {second_number} = {first_number - second_number}"
    elif command == 'multiply':
        return f"{first_number} × {second_number} = {first_number * second_number}"
    elif command == 'divide':
        if second_number == 0:
            return "Cannot divide by zero."
        return f"{first_number} ÷ {second_number} = {first_number / second_number}"
    elif command == 'pow':
        return f"{first_number} ^ {second_number} = {math.pow(first_number, second_number):.6f}"
    return "Unknown command."

# Callback query handler for inline buttons
async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    callback_data = query.data

    callback_map = {
        'help_command': help_command,
        'stats': stats,
        'cancel': cancel,
        'add': lambda u, c: two_number_entry(u, c, 'add'),
        'subtract': lambda u, c: two_number_entry(u, c, 'subtract'),
        'multiply': lambda u, c: two_number_entry(u, c, 'multiply'),
        'divide': lambda u, c: two_number_entry(u, c, 'divide'),
        'pow': lambda u, c: two_number_entry(u, c, 'pow'),
        'square': lambda u, c: one_number_entry(u, c, 'square'),
        'sin': lambda u, c: one_number_entry(u, c, 'sin'),
        'cos': lambda u, c: one_number_entry(u, c, 'cos'),
        'tan': lambda u, c: one_number_entry(u, c, 'tan'),
        'sqrt': lambda u, c: one_number_entry(u, c, 'sqrt'),
        'log': lambda u, c: one_number_entry(u, c, 'log'),
        'abs': lambda u, c: one_number_entry(u, c, 'abs'),
        'round': lambda u, c: one_number_entry(u, c, 'round'),
    }

    if callback_data in callback_map:
        await callback_map[callback_data](update, context)
    else:
        await query.message.reply_text("Unknown action.")
        await query.answer()

async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Unknown command. Try /help to see available commands.")

# Main function to run the bot
def main():
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN not set")
        return

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Register conversation handlers
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start), CommandHandler("help", help_command)],
        states={
            FIRST_NUMBER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, first_number_received),
            ],
            SECOND_NUMBER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, second_number_received),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Add command and callback query handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(callback_query_handler))
    app.add_handler(conversation_handler)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown_command))

    # Start the bot
    app.run_polling()

if __name__ == '__main__':
    main()
