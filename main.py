import logging
import os
from dotenv import load_dotenv
import asyncio
import random
import string
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Load environmental variables
load_dotenv()

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
    )

logger = logging.getLogger(__name__)

# Telegram API credentials
api_id = os.getenv("TELEGRAM_API_ID")
LENGTH, SYMBOLS, NUMBERS = range(3)

async def start(update: Update, context:ContextTypes.DEFAULT_TYPE):
    '''
    Starts the bot
    '''   
    await update.message.reply_text("welcome. The bot will prompt you in 3 seconds")
    await asyncio.sleep(3)
    await update.message.reply_text("How many characters should it have? Minimum is 8 characters.")
    return LENGTH
    
async def get_length(update: Update, context:ContextTypes.DEFAULT_TYPE):
    '''
    Starts the generation sequence
    '''
    raw_length = update.message.text.strip()

    if raw_length.isdigit():
        length = int(raw_length)
        if length >= 8:
            context.user_data["length"] = length
            await update.message.reply_text("Would like to include symbols? Type 'Yes' or 'no'")
            return SYMBOLS
        else:
            await update.message.reply_text("Invalid length. Try again")
            return LENGTH
    else:
        await update.message.reply_text("Invalid length. Try again")
        return LENGTH


async def with_symbol(update:Update, context:ContextTypes.DEFAULT_TYPE):
    '''
    Asks if the user will use symbols or not
    '''
    symbol = update.message.text.strip()

    if symbol.lower() == "yes" or symbol.lower() == "no":
        context.user_data["symbol"] = symbol.lower()
        await update.message.reply_text("Would like to include numbers? Type 'Yes' or 'no'")
        return NUMBERS
    else:
        await update.message.reply_text("Invalid response. Try again")
        return SYMBOLS
    
async def with_numbers(update:Update, context:ContextTypes.DEFAULT_TYPE):
    '''
    Asks if the user will use numbers or not
    '''
    raw_number = update.message.text.strip()
    number = raw_number.lower()
    if number in ["yes", "no"]:
        context.user_data["number"] = number.lower()
        await generate(update, context)
        return ConversationHandler.END
    else:
        await update.message.reply_text("Invalid response. Try again")
        return NUMBERS
    

async def generate(update:Update, context:ContextTypes.DEFAULT_TYPE):
    '''
    Generates the password
    '''
    print("I am here")
    await update.message.reply_text("Your password is being generated")
    length = context.user_data["length"]
    symbol = context.user_data["symbol"]
    number = context.user_data["number"]

    let_choice = list(string.ascii_letters)
    sym_choice = list(string.punctuation)
    num_choice = list(string.digits)

    if symbol == "yes" and number == "no":
        choice = let_choice + sym_choice
    elif symbol == "no" and number == "yes":
        choice = let_choice + num_choice
    elif symbol == "yes" and number == "yes":
        choice = let_choice + num_choice + sym_choice
    else:
        choice = let_choice
        
    password = ''.join(random.choices(choice, k=length))

    await update.message.reply_text(f"Your password is {password}")
    
    
async def cancel(update:Update, context:ContextTypes.DEFAULT_TYPE):
    '''
    Cancels the chat
    '''
    await update.message.reply_text("Conversations cancelled")

async def main():
    '''
    Main function to run the bot
    '''
    app = Application.builder().token(api_id).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LENGTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_length)],
            SYMBOLS: [MessageHandler(filters.TEXT & ~filters.COMMAND, with_symbol)],
            NUMBERS: [MessageHandler(filters.TEXT & ~filters.COMMAND, with_numbers)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(conv_handler)
    await app.run_polling()

if __name__ == '__main__':
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.run(main())