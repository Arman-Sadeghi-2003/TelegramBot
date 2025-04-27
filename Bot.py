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
import asyncio
import os
import math
from collections import defaultdict

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
    if update.callback_query:
        await update.callback_query.message.reply_text(
            f"👋 Hello {username}! I'm your friendly math assistant.\nAvailable commands:",
            reply_markup=reply_markup
        )
        await update.callback_query.answer()
    else:
        await update.message.reply_text(
            f"👋 Hello {username}! I'm your friendly math assistant.\nAvailable commands:",
            reply_markup=reply_markup
        )

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
    if update.callback_query:
        await update.callback_query.message.reply_text("Operation canceled.")
        await update.callback_query.answer()
    else:
        await update.message.reply_text("Operation canceled.")
    return ConversationHandler.END

# Conversation handler for commands requiring one number
async def one_number_entry(update: Update, context: ContextTypes.DEFAULT_TYPE, command: str):
    command_stats[command] += 1
    context.user_data['command'] = command
    if update.callback_query:
        await update.callback_query.message.reply_text("Please enter a number:")
        await update.callback_query.answer()
    else:
        await update.message.reply_text("Please enter a number:")
    return FIRST_NUMBER

async def one_number_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        number = float(update.message.text)
        command = context.user_data.get('command')
        if command == 'square':
            await update.message.reply_text(f"{number}² = {number * number}")
        elif command == 'sin':
            await update.message.reply_text(f"sin({number}) = {math.sin(number):.6f}")
        elif command == 'cos':
            await update.message.reply_text(f"cos({number}) = {math.cos(number):.6f}")
        elif command == 'tan':
            try:
                result = math.tan(number)
                await update.message.reply_text(f"tan({number}) = {result:.6f}")
            except ValueError:
                await update.message.reply_text("Error: Invalid input for tangent")
        elif command == 'sqrt':
            if number < 0:
                await update.message.reply_text("Cannot take square root of a negative number.")
            else:
                await update.message.reply_text(f"√{number} = {math.sqrt(number):.6f}")
        elif command == 'log':
            if number <= 0:
                await update.message.reply_text("Cannot take log of non-positive number.")
            else:
                await update.message.reply_text(f"ln({number}) = {math.log(number):.6f}")
        elif command == 'abs':
            await update.message.reply_text(f"|{number}| = {abs(number)}")
        elif command == 'round':
            await update.message.reply_text(f"round({number}) = {round(number)}")
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("Please enter a valid number.")
        return FIRST_NUMBER

# Conversation handler for commands requiring two numbers
async def two_number_entry(update: Update, context: ContextTypes.DEFAULT_TYPE, command: str):
    command_stats[command] += 1
    context.user_data['command'] = command
    if update.callback_query:
        await update.callback_query.message.reply_text("Please enter the first number:")
        await update.callback_query.answer()
    else:
        await update.message.reply_text("Please enter the first number:")
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
        if command == 'add':
            await update.message.reply_text(f"{first_number} + {second_number} = {first_number + second_number}")
        elif command == 'subtract':
            await update.message.reply_text(f"{first_number} - {second_number} = {first_number - second_number}")
        elif command == 'multiply':
            await update.message.reply_text(f"{first_number} × {second_number} = {first_number * second_number}")
        elif command == 'divide':
            if second_number == 0:
                await update.message.reply_text("Cannot divide by zero.")
            else:
                await update.message.reply_text(f"{first_number} ÷ {second_number} = {first_number / second_number}")
        elif command == 'pow':
            await update.message.reply_text(f"{first_number} ^ {second_number} = {math.pow(first_number, second_number):.6f}")
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("Please enter a valid number.")
        return SECOND_NUMBER

# Callback query handler for inline buttons
async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    callback_data = query.data

    # Map callback_data to the corresponding command function or conversation entry
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

    # Conversation handler for commands requiring one number
    one_number_conv = ConversationHandler(
        entry_points=[
            CommandHandler('square', lambda u, c: one_number_entry(u, c, 'square')),
            CommandHandler('sin', lambda u, c: one_number_entry(u, c, 'sin')),
            CommandHandler('cos', lambda u, c: one_number_entry(u, c, 'cos')),
            CommandHandler('tan', lambda u, c: one_number_entry(u, c, 'tan')),
            CommandHandler('sqrt', lambda u, c: one_number_entry(u, c, 'sqrt')),
            CommandHandler('log', lambda u, c: one_number_entry(u, c, 'log')),
            CommandHandler('abs', lambda u, c: one_number_entry(u, c, 'abs')),
            CommandHandler('round', lambda u, c: one_number_entry(u, c, 'round')),
        ],
        states={
            FIRST_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, one_number_received)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # Conversation handler for commands requiring two numbers
    two_number_conv = ConversationHandler(
        entry_points=[
            CommandHandler('add', lambda u, c: two_number_entry(u, c, 'add')),
            CommandHandler('subtract', lambda u, c: two_number_entry(u, c, 'subtract')),
            CommandHandler('multiply', lambda u, c: two_number_entry(u, c, 'multiply')),
            CommandHandler('divide', lambda u, c: two_number_entry(u, c, 'divide')),
            CommandHandler('pow', lambda u, c: two_number_entry(u, c, 'pow')),
        ],
        states={
            FIRST_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, first_number_received)],
            SECOND_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, second_number_received)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # Add handlers
    app.add_handler(one_number_conv)
    app.add_handler(two_number_conv)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CallbackQueryHandler(callback_query_handler))
    app.add_handler(MessageHandler(filters.COMMAND, unknown_command))

    print("MathMasterBot is running...")
    app.run_polling()

# Run the bot
if __name__ == "__main__":
    main()
