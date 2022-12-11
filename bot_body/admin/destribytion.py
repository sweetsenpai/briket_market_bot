from telegram.ext import (ConversationHandler, ContextTypes)
from telegram import (Update)
from briket_DB.sql_main_files.customers import read_all
from text_integration.pastebin_integration import get_text_api
from bot_body.functional_key import admin_keyboard
import asyncio
TEXT_DIST = range(1)


async def get_text_destribution(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text=get_text_api('mHKEnYh7'))
    return TEXT_DIST


async def start_distribution(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text_distribution = update.message.text
    await update.message.reply_text(text=get_text_api('n3M4zWjt'))
    await admin_keyboard(update, context)
    context.application.create_task(
        asyncio.gather(
            *(
                    context.bot.send_message(
                        chat_id=customer['chat_id'], text=text_distribution
                    )
                for customer in read_all()
            ), return_exceptions=True
        )
    )
    await update.message.reply_text(text='Рассылка успешно завершена')

    return ConversationHandler.END


async def cov_end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return ConversationHandler.END



