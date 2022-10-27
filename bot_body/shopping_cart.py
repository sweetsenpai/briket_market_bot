import logging
from briket_DB.residents import delet_on_phone
from briket_DB.config import mongodb
from bot_body.menu import dish_card_keyboard
from briket_DB.shcart_db import (add_dish, remove_dish,
                                 show_cart, empty_shcart,
                                 red_order, show_red_dish)

from briket_DB.order_db import (push_order, client_info,
                                tech_support, accept_order,
                                decline_order, finish_order)
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
    cancel_order = InlineKeyboardButton(text='Очистить корзину', callback_data='empty_cart')
    back = InlineKeyboardButton(text='◀️Назад', switch_inline_query_current_chat='')
    res = InlineKeyboardMarkup([[take_away, delivery], [red_order, cancel_order], [back]])
    return res


async def call_back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    cb_data = query.data.split(',')
    logger.info(
        "Callback data: {}".format(cb_data)
    )
    if cb_data[0] == 'add':
        add_dish(user_id=query.from_user.id, resident=cb_data[1], dish=cb_data[2], price=cb_data[3])
        await update.callback_query.edit_message_reply_markup(
            reply_markup=dish_card_keyboard(user_id=query.from_user.id, resident=cb_data[1], dish=cb_data[2], price=cb_data[3]))
        await query.answer()
        return
    elif cb_data[0] == 'minus':
        remove_dish(user_id=query.from_user.id, resident=cb_data[1], dish=cb_data[2])
        await update.callback_query.edit_message_reply_markup(
            reply_markup=dish_card_keyboard(user_id=query.from_user.id, resident=cb_data[1], dish=cb_data[2],
                                            price=cb_data[3]))
        await query.answer()
        return
    elif cb_data[0] == 'cart':
        await query.edit_message_text(text=show_cart(user_id=query.from_user.id),
                                      reply_markup=cart_inline())
        await query.answer()
        return
    elif cb_data[0] == 'red_order':
        await red_order(user_id=query.from_user.id, update=update)
        await query.answer()
        return
    elif cb_data[0] == 'show_red_dish':
        await show_red_dish(resident=cb_data[1], dish=cb_data[2], user_id=query.from_user.id,update=update)
        await query.answer()
        return
    elif cb_data[0] == 'empty_cart':
        await empty_shcart(user_id=query.from_user.id, update=update)
        await query.answer()
        return
    elif cb_data[0] == 'Доставка' or cb_data[0] == 'Самовывоз':
        await query.answer()
        await push_order(user_id=query.from_user.id, context=context, receipt_type=cb_data[0], update=update)
        return
    elif cb_data[0] == 'accept':
        await accept_order(order_num=int(cb_data[1]), update=update, resident=cb_data[2])
        await query.answer()
        return
    elif cb_data[0] == 'decline_order':
        await decline_order(order_num=int(cb_data[1]), update=update, resident=cb_data[2])
        await query.answer()
    elif cb_data[0] == 'support':
        await tech_support(context=context, msg_chat=update.callback_query.from_user.id)
        await query.answer()
        return
    elif cb_data[0] == 'client':
        await client_info(order_num=int(cb_data[1]), context=context, msg_chat=update.callback_query.from_user.id)
        await query.answer()
        return
    elif cb_data[0] == 'finish_order':
        await finish_order(order_num=int(cb_data[1]), update=update, resident=cb_data[2], context=context)
        await query.answer()
        return
    elif cb_data[0] == 'del_resident':
        delet_on_phone(cb_data[1])
        await update.callback_query.edit_message_text(text='Резидент успешно удален!')
        return
    elif cb_data[0] == 'del_admin':
        mongodb.admin.delete_one({"phone": cb_data[1]})
        await update.callback_query.edit_message_text(text='Администратор успешно удален!')
        return

