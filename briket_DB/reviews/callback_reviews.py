
from telegram import (InlineQueryResultArticle,
                      InputTextMessageContent,
                      Update,
                      InlineKeyboardMarkup,
                      InlineKeyboardButton, constants)
from briket_DB.reviews.reviews_main import read_revie


def review_inline(page, resident):
    back = InlineKeyboardButton(text='<<', callback_data=f'show_rev,{resident} ,{page-1}')
    forward = InlineKeyboardButton(text='>>', callback_data=f'show_rev,{resident}, {page+1}')
    if read_revie(comment_num=page-1, resident_name=resident) is False:
        keyboard = InlineKeyboardMarkup([[forward]])
        return keyboard
    elif read_revie(comment_num=page+1, resident_name=resident) is False:
        keyboard = InlineKeyboardMarkup([[back]])
        return keyboard
    keyboard = InlineKeyboardMarkup([[back, forward]])
    return keyboard


async def show_review(update: Update, resident_name, page=0):
    text = read_revie(resident_name=resident_name, comment_num=int(page))
    await update.callback_query.edit_message_text(text=text,
                                                  reply_markup=review_inline(int(page), resident=resident_name))
    return