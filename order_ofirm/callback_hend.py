from telegram import (InlineQueryResultArticle,
                      InputTextMessageContent,
                      Update, ReplyKeyboardMarkup, KeyboardButton)
from telegram.ext import ContextTypes


async def make_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    button1 = KeyboardButton(text='Самовывоз')
    button2 = KeyboardButton(text='Доставка')
    key = ReplyKeyboardMarkup(keyboard=[[button1], [button2]])
    msg_id = update.callback_query.from_user.id
    await context.bot.send_message(text='Выберете способ получения',
                                   reply_markup=key,
                                   chat_id=msg_id)
    return
