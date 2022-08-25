import logging
from uuid import uuid4
from telegram import (InlineQueryResultArticle,
                      InputTextMessageContent,
                      Update,
                      InlineKeyboardMarkup,
                      InlineKeyboardButton)
from telegram.ext import ContextTypes
from briket_DB.residents import read_all
from parcer.parcer_sheet import get_market_categories, get_dishs
import re

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(text='Понятно, хочу есть!',
                                      switch_inline_query_current_chat='')]]
    reply = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        text='Скорее нажимай на кнопку «Хочу есть» и выбирай блюда от резидентов фуд-корта «Брикет Маркет»!',
        reply_markup=reply)
    return


def inline_generator(resident: str) -> InlineKeyboardMarkup:

    categories = get_market_categories(resident)
    keyboard = []

    for category in categories:
        keyboard.append(
            InlineKeyboardButton(
                text=category,
                switch_inline_query_current_chat=' #/{}/{}'.format(resident, category)
            )
        )

    reply = InlineKeyboardMarkup([keyboard])
    return reply


def dish_card(resident: str, dish: str) -> InlineKeyboardMarkup:
    keyboard = []
    reply = InlineKeyboardMarkup([keyboard])
    return reply


async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.inline_query.query
    if query == "":
        results = []
        for market in read_all():
            results.append(
                InlineQueryResultArticle(
                    id=str(uuid4()),
                    title=market['resident_name'],
                    description=market['description'],
                    input_message_content=InputTextMessageContent('---------------------------------------------- '),
                    thumb_url=market['img_url'],
                    thumb_width=50,
                    thumb_height=50,
                    reply_markup=inline_generator(market['resident_name'])
                ))
        await update.inline_query.answer(results)
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
                    input_message_content=InputTextMessageContent('Отличная еда по приятной цене!'),
                    thumb_url=dish[3],
                    thumb_height=50,
                    thumb_width=50
                )
            )
        await update.inline_query.answer(answer)





