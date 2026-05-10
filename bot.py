import os
import re
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = os.getenv("BOT_TOKEN", "8632838449:AAGBW4zv7z895WPZKsY1ITVCQfcvTQSqKp8")

def format_number(number):
    """Formats a number with thousand separators."""
    if isinstance(number, (int, float)):
        return "{:,}".format(number)
    return str(number)

def safe_eval(expr):
    """Safely evaluates a mathematical expression."""
    # Allow only safe characters
    if not re.match(r'^[\d\+\-\*\/\(\)\.\^\s]*$', expr):
        return None
    
    # Replace ^ with ** for Python's power operator
    expr = expr.replace('^', '**')
    
    try:
        # Use a restricted environment for eval
        result = eval(expr, {"__builtins__": None}, {})
        return result
    except Exception:
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🎉 Welcome to Yukii Calculator Bot!\n\n"
        "✅ You can now use all calculator commands in DM.\n"
        "📌 Supported operations:\n"
        "➕ Addition (+)\n"
        "➖ Subtraction (-)\n"
        "✖️ Multiplication (*)\n"
        "➗ Division (/)\n"
        "🔢 Parentheses ( )\n"
        "⬆️ Exponentiation (^)\n\n"
        "💡 Example: 2+3*5 or (10+2)^2"
    )
    await update.message.reply_text(welcome_text)

async def calculate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    expr = update.message.text.strip()
    
    # Check if it looks like a math expression
    if not any(char in expr for char in "0123456789"):
        return

    result = safe_eval(expr)
    
    if result is not None:
        formatted_result = format_number(result)
        text = f"{expr} = {formatted_result}"
        
        keyboard = [
            [
                InlineKeyboardButton("📋 Copy", callback_data=f"copy_{formatted_result}"),
                InlineKeyboardButton("❌ Delete", callback_data="delete")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(text, reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "delete":
        await query.message.delete()
    elif query.data.startswith("copy_"):
        result_val = query.data.split("_")[1]
        await query.answer(f"Result: {result_val}", show_alert=True)

async def main():
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), calculate))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    print("Bot is running...")
    async with application:
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        # Run until the program is stopped
        while True:
            await asyncio.sleep(1)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
