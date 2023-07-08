from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes


async def add_new_worker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    join_button = InlineKeyboardButton(text='Начать получать заказы',
                                       url=f'https://t.me/briket_test_bot?start={update.message.chat_id}')
    await update.message.reply_text(text='Отправте данное сообщение новому сотруднику и он сможет начнет принемать заказы.',
                                    reply_markup=InlineKeyboardMarkup([[join_button]]))
    return
