import telegram.error
from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters, ContextTypes)
from telegram import (Update)
from briket_DB.customers import read_all
from text_integration.pastebin_integration import get_text_api
from time import sleep
import asyncio
TEXT_DIST = range(1)


async def get_text_destribution(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text=get_text_api('mHKEnYh7'))
    return TEXT_DIST


async def start_distribution(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text_distribution = update.message.text
    await update.message.reply_text(text=get_text_api('n3M4zWjt'))
    context.application.create_task(
        asyncio.gather(
            *(
                context.bot.send_message(
                    chat_id=customer['chat_id'], text=text_distribution, rate_limit_args={'priority': -1}
                )
                for customer in read_all()
            )
        )
    )
    return ConversationHandler.END


async def cov_end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return ConversationHandler.END



