import asyncio
import os
import math
from collections import defaultdict
from uuid import uuid4
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

# Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
NUMBER_INPUT = range(1)

# Command usage statistics
command_stats = defaultdict(int)

class MathOperation:
    """Base class for math operations"""
    def __init__(self, name, num_inputs, description):
        self.name = name
        self.num_inputs = num_inputs
        self.description = description
    
    async def execute(self, numbers):
        raise NotImplementedError

    async def format_result(self, numbers, result):
        return f"{self.name}({', '.join(map(str, numbers))}) = {result:.6f}"

class SingleNumberOperation(MathOperation):
    """Operations requiring one number"""
    def __init__(self, name, func, description, error_condition=None, error_message=None):
        super().__init__(name, 1, description)
        self.func = func
        self.error_condition = error_condition
        self.error_message = error_message

    async def execute(self, numbers):
        number = numbers[0]
        if self.error_condition and self.error_condition(number):
            raise ValueError(self.error_message)
        return self.func(number)

class TwoNumberOperation(MathOperation):
    """Operations requiring two numbers"""
    def __init__(self, name, func, description, error_condition=None, error_message=None, format_string=None):
        super().__init__(name, 2, description)
        self.func = func
        self.error_condition = error_condition
        self.error_message = error_message
        self.format_string = format_string

    async def execute(self, numbers):
        x, y = numbers
        if self.error_condition and self.error_condition(y):
            raise ValueError(self.error_message)
        try:
            return self.func(x, y)
        except Exception as e:
            raise ValueError(f"Error during calculation: {e}")
        async def format_result(self, numbers, result):
            if self.format_string:
                return self.format_string.format(*numbers, result)
            return super().format_result(numbers, result)

# Command registry
COMMANDS = {
    'square': SingleNumberOperation('square', lambda x: x * x, 'Square a number'),
    'sin': SingleNumberOperation('sin', math.sin, 'Calculate sine (in radians)'),
    'cos': SingleNumberOperation('cos', math.cos, 'Calculate cosine (in radians)'),
    'tan': SingleNumberOperation('tan', math.tan, 'Calculate tangent (in radians)', 
                               lambda x: math.cos(x) == 0, 'Invalid input for tangent'),
    'sqrt': SingleNumberOperation('sqrt', math.sqrt, 'Square root', 
                                lambda x: x < 0, 'Cannot take square root of a negative number'),
    'log': SingleNumberOperation('log', math.log, 'Natural logarithm (ln)', 
                               lambda x: x <= 0, 'Cannot take log of non-positive number'),
    'abs': SingleNumberOperation('abs', abs, 'Absolute value'),
    'round': SingleNumberOperation('round', round, 'Round to nearest integer'),
    'add': TwoNumberOperation('add', lambda x, y: x + y, 'Add two numbers', 
                            format_string='{} + {} = {}'),
    'subtract': TwoNumberOperation('subtract', lambda x, y: x - y, 'Subtract two numbers',
                                 format_string='{} - {} = {}'),
    'multiply': TwoNumberOperation('multiply', lambda x, y: x * y, 'Multiply two numbers',
                                 format_string='{} × {} = {}'),
    'divide': TwoNumberOperation('divide', lambda x, y: x / y, 'Divide two numbers',
                               lambda y: y == 0, 'Cannot divide by zero',
                               format_string='{} ÷ {} = {}'),
    'pow': TwoNumberOperation(
        'pow',
        math.pow,
        'x raised to the power y',
        error_condition=lambda y: False,  # You could define your own rules here
        error_message='Invalid input for pow'
    ),
}

class MathBot:
    def __init__(self):
        self.app = ApplicationBuilder().token(BOT_TOKEN).build()
        self.setup_handlers()

    @staticmethod
    def create_keyboard():
        """Create the command keyboard"""
        buttons = [
            [InlineKeyboardButton("/help", callback_data='help')],
            [InlineKeyboardButton("/add", callback_data='add'), 
             InlineKeyboardButton("/subtract", callback_data='subtract')],
            [InlineKeyboardButton("/multiply", callback_data='multiply'), 
             InlineKeyboardButton("/divide", callback_data='divide')],
            [InlineKeyboardButton("/sin", callback_data='sin'), 
             InlineKeyboardButton("/cos", callback_data='cos'), 
             InlineKeyboardButton("/tan", callback_data='tan')],
            [InlineKeyboardButton("/square", callback_data='square')],
            [InlineKeyboardButton("/sqrt", callback_data='sqrt'), 
             InlineKeyboardButton("/pow", callback_data='pow')],
            [InlineKeyboardButton("/log", callback_data='log'), 
             InlineKeyboardButton("/abs", callback_data='abs'), 
             InlineKeyboardButton("/round", callback_data='round')],
            [InlineKeyboardButton("/stats", callback_data='stats')],
            [InlineKeyboardButton("/Cancel", callback_data='cancel')]
        ]
        return InlineKeyboardMarkup(buttons)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        command_stats['start'] += 1
        username = update.effective_user.first_name or "there"
        message = f"👋 Hello {username}! I'm your friendly math assistant.\nAvailable commands:"
        reply_markup = self.create_keyboard()
        
        if update.callback_query:
            await update.callback_query.message.reply_text(message, reply_markup=reply_markup)
            await update.callback_query.answer()
        else:
            await update.message.reply_text(message, reply_markup=reply_markup)

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        command_stats['help'] += 1
        help_text = "📚 MathMasterBot Commands:\n/start - Welcome message\n"
        help_text += '\n'.join(f"/{name} - {op.description}" for name, op in COMMANDS.items())
        help_text += "\n/stats - Show command usage statistics\n/cancel - Cancel the current operation"
        
        if update.callback_query:
            await update.callback_query.message.reply_text(help_text)
            await update.callback_query.answer()
        else:
            await update.message.reply_text(help_text)

    async def stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        command_stats['stats'] += 1
        stats_message = "📊 Command Usage Statistics:\n"
        stats_message += '\n'.join(f"/{cmd}: {count} times" for cmd, count in command_stats.items())
        
        if update.callback_query:
            await update.callback_query.message.reply_text(stats_message)
            await update.callback_query.answer()
        else:
            await update.message.reply_text(stats_message)

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        command_stats['cancel'] += 1
        message = "Operation canceled."
        if update.callback_query:
            await update.callback_query.message.reply_text(message)
            await update.callback_query.answer()
        else:
            await update.message.reply_text(message)
        return ConversationHandler.END

    async def math_operation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        command = query.data
        if command not in COMMANDS:
            await query.message.reply_text("Unknown action.")
            await query.answer()
            return

        command_stats[command] += 1
        context.user_data['command'] = command
        context.user_data['numbers'] = []
        await query.message.reply_text(f"Please enter the first number for {command}:")
        await query.answer()
        return NUMBER_INPUT

    async def number_received(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            number = float(update.message.text)
            command = context.user_data.get('command')
            numbers = context.user_data.get('numbers', [])
            numbers.append(number)
            operation = COMMANDS[command]
    
            if len(numbers) < operation.num_inputs:
                await update.message.reply_text(f"Please enter the {'second' if len(numbers) == 1 else 'next'} number:")
                context.user_data['numbers'] = numbers
                return NUMBER_INPUT
    
            result = await operation.execute(numbers)
            formatted_result = await operation.format_result(numbers, result)
            await update.message.reply_text(formatted_result)
            context.user_data.clear()
            return ConversationHandler.END
    
        except ValueError as e:
            await update.message.reply_text(str(e))
            return NUMBER_INPUT

        except ValueError:
            await update.message.reply_text("Invalid input, please enter a valid number.")
            return NUMBER_INPUT

    def setup_handlers(self):
        """Set up the command handlers"""
        conv_handler = ConversationHandler(
            entry_points=[
                CallbackQueryHandler(self.math_operation, pattern='^(add|subtract|multiply|divide|square|sqrt|log|sin|cos|tan|round|pow|abs)$'),
            ],
            states={
                NUMBER_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.number_received)]
            },
            fallbacks=[CommandHandler('cancel', self.cancel)]
        )

        self.app.add_handler(conv_handler)
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("help", self.help))
        self.app.add_handler(CommandHandler("stats", self.stats))
        self.app.add_handler(CallbackQueryHandler(self.cancel, pattern='^cancel$'))


    def run(self):
        """Run the bot"""
        self.app.run_polling()

# Start the bot
if __name__ == '__main__':
    math_bot = MathBot()
    math_bot.run()
