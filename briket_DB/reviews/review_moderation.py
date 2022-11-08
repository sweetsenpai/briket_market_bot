from briket_DB.reviews.reviews_main import reviews_db
from briket_DB.order_db import admin
from telegram import (
                      Update,
                      InlineKeyboardMarkup,
                      InlineKeyboardButton,)
from telegram.ext import ContextTypes


def rev_inline(user_id, resident_name):
    accept = InlineKeyboardButton(text='Опубликовать', callback_data=f'publish_rev,{user_id},{resident_name}')
    decline = InlineKeyboardButton(text='Удалить', callback_data=f'delete_rev,{user_id},{resident_name}')
    in_key = InlineKeyboardMarkup([[accept, decline]])
    return in_key


async def admin_new_rev(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id, resident):
    revie = reviews_db.find_one({'resident': resident})['on_moderation']
    print(revie)
    user_name = revie[str(user_id)]['user_name']
    text = revie[user_id]['text']
    msg = '<b>НОВЫЙ ОТЗЫВ!</b>\n' \
          'Резидент: {}\n' \
          'Пользователь:{}\n' \
          '{}'.format(resident, user_name, text)
    for ad in admin.find():
        try:
            await context.bot.sendMessage(chat_id=ad['chat_id'], text=msg,
                                          reply_markup=rev_inline(user_id=user_id, resident_name=resident),
                                          parse_mode='HTML')
        except KeyError:
            continue

    return
