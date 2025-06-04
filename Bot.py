import asyncio
import os
import math
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import List, Optional, Callable, Any
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


class Config:
    """Configuration class for bot settings"""
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    NUMBER_INPUT = range(1)


class StatisticsManager:
    """Manages command usage statistics"""
    
    def __init__(self):
        self._stats = defaultdict(int)
    
    def increment(self, command: str) -> None:
        """Increment usage count for a command"""
        self._stats[command] += 1
    
    def get_stats(self) -> dict:
        """Get all statistics"""
        return dict(self._stats)
    
    def get_formatted_stats(self) -> str:
        """Get formatted statistics string"""
        if not self._stats:
            return "📊 No commands have been used yet."
        
        stats_message = "📊 Command Usage Statistics:\n"
        stats_message += '\n'.join(f"/{cmd}: {count} times" for cmd, count in self._stats.items())
        return stats_message


class MathOperation(ABC):
    """Abstract base class for math operations"""
    
    def __init__(self, name: str, num_inputs: int, description: str):
        self.name = name
        self.num_inputs = num_inputs
        self.description = description
    
    @abstractmethod
    async def execute(self, numbers: List[float]) -> float:
        """Execute the mathematical operation"""
        pass
    
    async def format_result(self, numbers: List[float], result: float) -> str:
        """Format the result for display"""
        return f"{self.name}({', '.join(map(str, numbers))}) = {result:.6f}"


class SingleNumberOperation(MathOperation):
    """Operations requiring one number"""
    
    def __init__(
        self,
        name: str,
        func: Callable[[float], float],
        description: str,
        error_condition: Optional[Callable[[float], bool]] = None,
        error_message: Optional[str] = None
    ):
        super().__init__(name, 1, description)
        self.func = func
        self.error_condition = error_condition
        self.error_message = error_message

    async def execute(self, numbers: List[float]) -> float:
        if len(numbers) != 1:
            raise ValueError(f"{self.name} requires exactly 1 number")
        
        number = numbers[0]
        if self.error_condition and self.error_condition(number):
            raise ValueError(self.error_message or f"Invalid input for {self.name}")
        
        try:
            return self.func(number)
        except Exception as e:
            raise ValueError(f"Error during {self.name} calculation: {e}")


class TwoNumberOperation(MathOperation):
    """Operations requiring two numbers"""
    
    def __init__(
        self,
        name: str,
        func: Callable[[float, float], float],
        description: str,
        error_condition: Optional[Callable[[float], bool]] = None,
        error_message: Optional[str] = None,
        format_string: Optional[str] = None
    ):
        super().__init__(name, 2, description)
        self.func = func
        self.error_condition = error_condition
        self.error_message = error_message
        self.format_string = format_string

    async def execute(self, numbers: List[float]) -> float:
        if len(numbers) != 2:
            raise ValueError(f"{self.name} requires exactly 2 numbers")
        
        x, y = numbers
        if self.error_condition and self.error_condition(y):
            raise ValueError(self.error_message or f"Invalid input for {self.name}")
        
        try:
            return self.func(x, y)
        except Exception as e:
            raise ValueError(f"Error during {self.name} calculation: {e}")

    async def format_result(self, numbers: List[float], result: float) -> str:
        if self.format_string:
            return self.format_string.format(*numbers, result)
        return await super().format_result(numbers, result)


class CommandRegistry:
    """Registry for all mathematical operations"""
    
    def __init__(self):
        self._commands = self._initialize_commands()
    
    def _initialize_commands(self) -> dict:
        """Initialize all available mathematical operations"""
        return {
            'square': SingleNumberOperation(
                'square', 
                lambda x: x * x, 
                'Square a number'
            ),
            'sin': SingleNumberOperation(
                'sin', 
                math.sin, 
                'Calculate sine (in radians)'
            ),
            'cos': SingleNumberOperation(
                'cos', 
                math.cos, 
                'Calculate cosine (in radians)'
            ),
            'tan': SingleNumberOperation(
                'tan', 
                math.tan, 
                'Calculate tangent (in radians)',
                lambda x: abs(math.cos(x)) < 1e-10,
                'Invalid input for tangent (undefined at π/2 + nπ)'
            ),
            'sqrt': SingleNumberOperation(
                'sqrt', 
                math.sqrt, 
                'Square root',
                lambda x: x < 0,
                'Cannot take square root of a negative number'
            ),
            'log': SingleNumberOperation(
                'log', 
                math.log, 
                'Natural logarithm (ln)',
                lambda x: x <= 0,
                'Cannot take log of non-positive number'
            ),
            'abs': SingleNumberOperation(
                'abs', 
                abs, 
                'Absolute value'
            ),
            'round': SingleNumberOperation(
                'round', 
                round, 
                'Round to nearest integer'
            ),
            'add': TwoNumberOperation(
                'add', 
                lambda x, y: x + y, 
                'Add two numbers',
                format_string='{} + {} = {:.6f}'
            ),
            'subtract': TwoNumberOperation(
                'subtract', 
                lambda x, y: x - y, 
                'Subtract two numbers',
                format_string='{} - {} = {:.6f}'
            ),
            'multiply': TwoNumberOperation(
                'multiply', 
                lambda x, y: x * y, 
                'Multiply two numbers',
                format_string='{} × {} = {:.6f}'
            ),
            'divide': TwoNumberOperation(
                'divide', 
                lambda x, y: x / y, 
                'Divide two numbers',
                lambda y: y == 0,
                'Cannot divide by zero',
                format_string='{} ÷ {} = {:.6f}'
            ),
            'pow': TwoNumberOperation(
                'pow',
                math.pow,
                'x raised to the power y',
                format_string='{} ^ {} = {:.6f}'
            ),
        }
    
    def get_command(self, name: str) -> Optional[MathOperation]:
        """Get a command by name"""
        return self._commands.get(name)
    
    def get_all_commands(self) -> dict:
        """Get all commands"""
        return self._commands.copy()
    
    def get_command_names(self) -> List[str]:
        """Get list of all command names"""
        return list(self._commands.keys())


class KeyboardManager:
    """Manages inline keyboard creation"""
    
    def __init__(self, command_registry: CommandRegistry):
        self.command_registry = command_registry
    
    def create_main_keyboard(self) -> InlineKeyboardMarkup:
        """Create the main command keyboard"""
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
            [InlineKeyboardButton("/cancel", callback_data='cancel')]
        ]
        return InlineKeyboardMarkup(buttons)


class MessageFormatter:
    """Handles message formatting"""
    
    @staticmethod
    def welcome_message(username: str) -> str:
        """Format welcome message"""
        return f"👋 Hello {username}! I'm your friendly math assistant.\nAvailable commands:"
    
    @staticmethod
    def help_message(command_registry: CommandRegistry) -> str:
        """Format help message"""
        help_text = "📚 MathMasterBot Commands:\n/start - Welcome message\n"
        commands = command_registry.get_all_commands()
        help_text += '\n'.join(f"/{name} - {op.description}" for name, op in commands.items())
        help_text += "\n/stats - Show command usage statistics\n/cancel - Cancel the current operation"
        return help_text
    
    @staticmethod
    def number_prompt(command: str, position: str = "first") -> str:
        """Format number input prompt"""
        return f"Please enter the {position} number for {command}:"
    
    @staticmethod
    def get_position_text(count: int) -> str:
        """Get position text for number input"""
        positions = {1: "second", 2: "third", 3: "fourth"}
        return positions.get(count, f"{count + 1}th")


class ConversationState:
    """Manages conversation state for each user"""
    
    def __init__(self):
        self.command: Optional[str] = None
        self.numbers: List[float] = []
    
    def reset(self):
        """Reset the conversation state"""
        self.command = None
        self.numbers = []
    
    def add_number(self, number: float):
        """Add a number to the conversation"""
        self.numbers.append(number)
    
    def is_complete(self, operation: MathOperation) -> bool:
        """Check if we have enough numbers for the operation"""
        return len(self.numbers) >= operation.num_inputs


class MathBot:
    """Main Telegram bot class"""
    
    def __init__(self):
        if not Config.BOT_TOKEN:
            raise ValueError("BOT_TOKEN environment variable is required")
        
        self.app = ApplicationBuilder().token(Config.BOT_TOKEN).build()
        self.stats_manager = StatisticsManager()
        self.command_registry = CommandRegistry()
        self.keyboard_manager = KeyboardManager(self.command_registry)
        self.message_formatter = MessageFormatter()
        
        self._setup_handlers()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        self.stats_manager.increment('start')
        username = update.effective_user.first_name or "there"
        message = self.message_formatter.welcome_message(username)
        reply_markup = self.keyboard_manager.create_main_keyboard()
        
        if update.callback_query:
            await update.callback_query.message.reply_text(message, reply_markup=reply_markup)
            await update.callback_query.answer()
        else:
            await update.message.reply_text(message, reply_markup=reply_markup)

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        self.stats_manager.increment('help')
        help_text = self.message_formatter.help_message(self.command_registry)
        
        if update.callback_query:
            await update.callback_query.message.reply_text(help_text)
            await update.callback_query.answer()
        else:
            await update.message.reply_text(help_text)

    async def stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command"""
        self.stats_manager.increment('stats')
        stats_message = self.stats_manager.get_formatted_stats()
        
        if update.callback_query:
            await update.callback_query.message.reply_text(stats_message)
            await update.callback_query.answer()
        else:
            await update.message.reply_text(stats_message)

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /cancel command"""
        self.stats_manager.increment('cancel')
        message = "❌ Operation canceled."
        
        if update.callback_query:
            await update.callback_query.message.reply_text(message)
            await update.callback_query.answer()
        else:
            await update.message.reply_text(message)
        
        context.user_data.clear()
        return ConversationHandler.END

    async def math_operation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle math operation selection"""
        query = update.callback_query
        command = query.data
        
        operation = self.command_registry.get_command(command)
        if not operation:
            await query.message.reply_text("❌ Unknown operation.")
            await query.answer()
            return ConversationHandler.END

        self.stats_manager.increment(command)
        
        # Initialize conversation state
        state = ConversationState()
        state.command = command
        context.user_data['conversation_state'] = state
        
        prompt = self.message_formatter.number_prompt(command, "first")
        await query.message.reply_text(prompt)
        await query.answer()
        return Config.NUMBER_INPUT

    async def number_received(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle number input"""
        try:
            number = float(update.message.text)
        except ValueError:
            await update.message.reply_text("❌ Invalid input, please enter a valid number.")
            return Config.NUMBER_INPUT
        
        state = context.user_data.get('conversation_state')
        if not state:
            await update.message.reply_text("❌ No active operation. Please start a new operation.")
            return ConversationHandler.END
        
        operation = self.command_registry.get_command(state.command)
        if not operation:
            await update.message.reply_text("❌ Unknown operation.")
            return ConversationHandler.END
        
        state.add_number(number)
        
        try:
            if state.is_complete(operation):
                # Execute the operation
                result = await operation.execute(state.numbers)
                formatted_result = await operation.format_result(state.numbers, result)
                await update.message.reply_text(f"✅ {formatted_result}")
                context.user_data.clear()
                return ConversationHandler.END
            else:
                # Ask for next number
                position = self.message_formatter.get_position_text(len(state.numbers))
                prompt = self.message_formatter.number_prompt(state.command, position)
                await update.message.reply_text(prompt)
                return Config.NUMBER_INPUT
                
        except ValueError as e:
            await update.message.reply_text(f"❌ {str(e)}")
            return Config.NUMBER_INPUT
        except Exception as e:
            await update.message.reply_text(f"❌ An unexpected error occurred: {str(e)}")
            context.user_data.clear()
            return ConversationHandler.END

    def _setup_handlers(self):
        """Set up all bot handlers"""
        # Conversation handler for math operations
        conv_handler = ConversationHandler(
            entry_points=[
                CallbackQueryHandler(
                    self.math_operation, 
                    pattern=f"^({'|'.join(self.command_registry.get_command_names())})$"
                ),
            ],
            states={
                Config.NUMBER_INPUT: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.number_received)
                ]
            },
            fallbacks=[
                CommandHandler('cancel', self.cancel),
                CallbackQueryHandler(self.cancel, pattern='^cancel$')
            ]
        )

        # Add handlers to application
        self.app.add_handler(conv_handler)
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("help", self.help))
        self.app.add_handler(CommandHandler("stats", self.stats))
        self.app.add_handler(CallbackQueryHandler(self.start, pattern='^help$'))
        self.app.add_handler(CallbackQueryHandler(self.stats, pattern='^stats$'))
        self.app.add_handler(CallbackQueryHandler(self.cancel, pattern='^cancel$'))

    def run(self):
        """Run the bot"""
        print("🤖 MathMasterBot is starting...")
        self.app.run_polling()


def main():
    """Main entry point"""
    try:
        bot = MathBot()
        bot.run()
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
    except Exception as e:
        print(f"❌ An error occurred: {e}")


if __name__ == '__main__':
    main()
