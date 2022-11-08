import logging
from uuid import uuid4
from telegram import (InlineQueryResultArticle,
                      InputTextMessageContent,
                      Update,
                      InlineKeyboardMarkup,
                      InlineKeyboardButton, constants)
from telegram.ext import ContextTypes
from briket_DB.residents import read_all
from parcer.parcer_sheet import get_market_categories, get_dishs
from briket_DB.shcart_db import get_dish_quantity
from text_integration.pastebin_integration import get_text_api
import gspread
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(text='Понятно, хочу есть!',
                                      switch_inline_query_current_chat='')]]
    reply = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        text=get_text_api('EJ7xbdY6'),
        reply_markup=reply)
    return


def inline_generator(resident: str) -> InlineKeyboardMarkup:

    categories = get_market_categories(resident)
    keyboard = []
    try:
        for category in categories:
                keyboard.append(
                   [(InlineKeyboardButton(
                        text=category,
                        switch_inline_query_current_chat='#/{}/{}'.format(resident, category)
                    ))]
                )
    except TypeError: pass

    revie = [InlineKeyboardButton(callback_data=f'reviews,{resident}', text='Отзывы')]
    send_revie = [InlineKeyboardButton(callback_data=f'send_revie,{resident}', text='Оставить отзыв')]
    rez2 = [InlineKeyboardButton(switch_inline_query_current_chat='', text='◀️Назад')]
    keyboard.append(revie)
    keyboard.append(send_revie)
    keyboard.append(rez2)
    reply = InlineKeyboardMarkup(keyboard)
    return reply


def dish_card_keyboard(resident: str, dish: str, price, user_id: int, query='') -> InlineKeyboardMarkup:
    rez1 = InlineKeyboardButton(callback_data=','.join(['add',
                                                        resident, dish, str(price)]),
                                text='{} ➕ Добавить в корзину'.format(
                                    get_dish_quantity(user_id=user_id, resident=resident, dish=dish)
                                ))
    rez2 = InlineKeyboardButton(switch_inline_query_current_chat=query,
                                text='◀️Назад')
    rez3 = InlineKeyboardButton(callback_data=','.join(['minus', resident, dish, str(price)]),
                                text='➖ Удалить')
    rez4 = InlineKeyboardButton(callback_data='cart',
                                text='Корзина')

    reply = InlineKeyboardMarkup([[rez1, rez3], [rez2, rez4]])
    return reply


async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.inline_query.query
    if query == "":
        results = []
        for market in read_all():
            try:
                results.append(
                    InlineQueryResultArticle(
                        id=str(uuid4()),
                        title=market['resident_name'],
                        description=market['description'],
                        input_message_content=InputTextMessageContent(
                            message_text='<b>{}</b>\n'
                                         '{}\n'
                                         '<a href="{}">‎</a>'.format(market['resident_name'], market['description'], market['img_url'],),
                            parse_mode='HTML',
                            disable_web_page_preview=False
                        ),
                        thumb_url=market['img_url'],
                        thumb_width=50,
                        thumb_height=50,
                        reply_markup=inline_generator(market['resident_name'])
                    ))
            except gspread.exceptions.WorksheetNotFound or KeyError:
                pass
        await update.inline_query.answer(results, cache_time=600)
    elif '#' in query:
        answer = []
        data = query.split('/')
        for dish in get_dishs(sheet=data[1], cat=data[2]):
            answer.append(
                InlineQueryResultArticle(
                    id=str(uuid4()),
                    title=dish[0],
                    description='Вес:{} гр.\n'
                                'Цена:{}'.format(dish[1], dish[2]),
                    input_message_content=InputTextMessageContent(
                        message_text='{}\n'
                                     'Вес: {} гр.\n'
                                     'Цена: {}'
                                     '<a href="{}">‎</a>'
                                     '\nБелки: {}\nЖиры: {}\nУглеводы: {}'.format(dish[7],dish[1], dish[2], dish[3],
                                                                                  dish[4], dish[5],dish[6]),
                        disable_web_page_preview=False,
                        parse_mode=constants.ParseMode.HTML
                        ),
                    reply_markup=dish_card_keyboard(query=query, resident=data[1], dish=dish[0], price=dish[2], user_id=update.inline_query.from_user.id),
                    thumb_url=dish[3],
                    thumb_height=50,
                    thumb_width=50
                )
            )
        await update.inline_query.answer(answer)





