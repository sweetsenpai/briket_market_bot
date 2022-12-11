
from telegram import (InlineQueryResultArticle,
                      InputTextMessageContent,
                      Update,
                      InlineKeyboardMarkup,
                      InlineKeyboardButton, constants)
from briket_DB.reviews.reviews_main import read_revie


def review_inline(page, resident):
    back = InlineKeyboardButton(text=' ◀️', callback_data=f'show_rev,{resident}, {page-1}')
    forward = InlineKeyboardButton(text=' ▶️', callback_data=f'show_rev,{resident}, {page+1}')
    back_menu = InlineKeyboardButton(text='Назад', callback_data='get_menu,{}'.format(resident))
    if read_revie(comment_num=page-1, resident_name=resident) is False or page == 0:
        keyboard = InlineKeyboardMarkup([[forward], [back_menu]])
        return keyboard
    elif read_revie(comment_num=page+1, resident_name=resident) is False:
        keyboard = InlineKeyboardMarkup([[back], [back_menu]])
        return keyboard
    keyboard = InlineKeyboardMarkup([[back, forward], [back_menu]])
    return keyboard


async def show_review(update: Update, resident_name, page=0):
    text = read_revie(resident_name=resident_name, comment_num=int(page))
    if text is not False:
        await update.callback_query.edit_message_text(text=text,
                                                      reply_markup=review_inline(int(page), resident=resident_name))
        return
    back_menu = InlineKeyboardButton(text='Назад', callback_data='get_menu,{}'.format(resident_name))
    await update.callback_query.edit_message_text(text='Пока-что тут нет отзывов.',
                                                  reply_markup=InlineKeyboardMarkup([[back_menu]]))
    return
