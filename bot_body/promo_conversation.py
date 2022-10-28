import logging
from briket_DB.promotions import chek_personal_code
from briket_DB.customers import find_id, create, update_addres, read_one
from telegram import ReplyKeyboardRemove, Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ContextTypes,
    ConversationHandler)
from text_integration.pastebin_integration import get_text_api
from briket_DB.promotions import chek_promo
PROMO = range(1)


async def promo_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text='Введите промокод :')
    return PROMO


async def promo_end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    promo = update.message.text
    check_result = chek_promo(promo_code=promo, user_id=update.message.chat_id)
    if check_result[1] is False:
        await update.message.reply_text(text=check_result[0])
        return ConversationHandler.END

    await update.message.reply_text(text=check_result)
    return ConversationHandler.END


async def skip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return ConversationHandler.END
