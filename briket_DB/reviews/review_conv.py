from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler, MessageHandler, filters, CommandHandler)
from bot_body.functional_key import customer_keyboard
from briket_DB.reviews.reviews_main import insert_moderation_revie, reviews_db, update_text, get_resident
from briket_DB.reviews.review_moderation import admin_new_rev

TEXT, LAST = range(2)


async def start_rev(update: Update, context: ContextTypes.DEFAULT_TYPE):
    key_list = []
    for resident in reviews_db.find():
        key_list.append([KeyboardButton(text=resident['resident'])])

    key = ReplyKeyboardMarkup(keyboard=key_list, one_time_keyboard=True)
    await update.message.reply_text(text='Выбери заведение на которое хочешь оставить отзыв,\n'
                                         'на клавиатуре ниже', reply_markup=key)
    return TEXT


async def text_rev(update: Update, context: ContextTypes.DEFAULT_TYPE):

    resident = update.message.text
    user_n = update.message.from_user.name
    user_id = update.message.from_user.id

    insert_moderation_revie(
        user_name=user_n,
        user_id=user_id,
        resident_name=resident,
        text='...'
    )
    await update.message.reply_text(text='Введи отзыв')
    return LAST


async def end_rev(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    update_text(user_id=update.message.from_user.id, text=msg)
    await admin_new_rev(update=update, context=context, user_id=update.message.from_user.id,
                        resident=get_resident(user_id=update.message.from_user.id,
                                              text=msg))
    await update.message.reply_text(text='Отзыв успешно отправлен!\n Он будет опубликован после модерации.')
    await customer_keyboard(update, context)
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text='Команда прервана')
    return ConversationHandler.END


