import logging
from briket_DB.shcart_db import add_dish, remove_dish, show_cart
from briket_DB.order_db import push_order, client_info, tech_support, order_status_up
from menu import dish_card_keyboard
from telegram import (Update,
                      InlineKeyboardMarkup,
                      InlineKeyboardButton)
from telegram.ext import ContextTypes
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def cart_inline():
    take_away = InlineKeyboardButton(text='Заберу сам', callback_data='Самовывоз')
    delivery = InlineKeyboardButton(text='Доставка', callback_data='Доставка')
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
        print(query.from_user.id)
        await update.callback_query.edit_message_reply_markup(
            reply_markup=dish_card_keyboard(user_id=query.from_user.id, resident=cb_data[1], dish=cb_data[2], price=cb_data[3]))
        await query.answer()
    elif cb_data[0] == 'minus':
        remove_dish(user_id=query.from_user.id, resident=cb_data[1], dish=cb_data[2])
        await update.callback_query.edit_message_reply_markup(
            reply_markup=dish_card_keyboard(user_id=query.from_user.id, resident=cb_data[1], dish=cb_data[2],
                                            price=cb_data[3]))
        await query.answer()
    elif cb_data[0] == 'cart':
        await query.edit_message_text(text=show_cart(query.from_user.id),
                                      reply_markup=cart_inline())
        await query.answer()
    elif cb_data[0] == 'Доставка' or cb_data[0] == 'Самовывоз':
        await query.answer()
        await push_order(user_id=query.from_user.id, context=context, receipt_type=cb_data[0])
    elif cb_data[0] == 'accept':
        await order_status_up(order_num=int(cb_data[1]), update=update)
        await query.answer()
    elif cb_data[0] == 'decline_order':
        await query.answer()
    elif cb_data[0] == 'support':
        await tech_support(context=context, msg_chat=update.callback_query.from_user.id)
        await query.answer()
    elif cb_data[0] == 'client':
        await client_info(int(cb_data[1]), context=context, msg_chat=update.callback_query.from_user.id)
        await query.answer()
    elif cb_data[0] == 'redaction_order':
        await query.answer()
