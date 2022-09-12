import logging
from briket_DB.shcart_db import add_dish, remove_dish, show_cart
from telegram import (Update,
                      InlineKeyboardMarkup,
                      InlineKeyboardButton,
                      Message)
from telegram.ext import ContextTypes, Application
from briket_DB.passwords import bot_key
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def cart_inline():
    take_away = InlineKeyboardButton(text='Заберу сам', callback_data='take_away')
    delivery = InlineKeyboardButton(text='Доставка', callback_data='delivery')
    comment = InlineKeyboardButton(text='Комментарий к заказу', callback_data='order_comment')
    red_order = InlineKeyboardButton(text='Редактор Заказа', callback_data='red_order')
    cancel_order = InlineKeyboardButton(text='Отменить заказ', callback_data='cancel_order')
    back = InlineKeyboardButton(text='◀️Назад', switch_inline_query_current_chat='')
    res = InlineKeyboardMarkup([[take_away, delivery], [comment], [red_order, cancel_order], [back]])
    return res


async def call_back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    cb_data = query.data.split(',')
    logger.info(
        "Callback data: {}".format(cb_data)
    )
    if cb_data[0] == 'add':
        add_dish(user_id=query.from_user.id, resident=cb_data[1], dish=cb_data[2], price=cb_data[3])
        await query.answer()
    elif cb_data[0] == 'minus':
        remove_dish(user_id=query.from_user.id, resident=cb_data[1], dish=cb_data[2])
        await query.answer()
    elif cb_data[0] == 'cart':
        await query.edit_message_text(text=show_cart(query.from_user.id),
                                      reply_markup=cart_inline())
    elif cb_data[0] == 'delivery':
        await context.bot.sendMessage(
            chat_id=58829330,
            text='Памагитя!!!!!!!!!!!'
        )
