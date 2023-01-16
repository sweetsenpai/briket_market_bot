from briket_DB.shopping.order_db import orders_db
from telegram import (
                      Update,
                      InlineKeyboardMarkup,
                      InlineKeyboardButton)
from briket_DB.shopping.shcart_db import add_dish
from parcer.parcer_sheet import get_one_dish


def po_inlinae(page, user_id, order_num):
    back = InlineKeyboardButton(text=' ◀️', callback_data='PO,{}'.format(page-1))
    forward = InlineKeyboardButton(text=' ▶️', callback_data='PO,{}'.format(page+1))
    repeat = InlineKeyboardButton(text='Повторить заказ', callback_data='repeat,{}'.format(order_num))
    if page == 0:
        keyboard = InlineKeyboardMarkup([[forward], [repeat]])
        return keyboard
    try:
        orders_db.find(filter={'user_id': user_id})[page+1]
    except IndexError:
        keyboard = InlineKeyboardMarkup([[back], [repeat]])
        return keyboard
    keyboard = InlineKeyboardMarkup([[back, forward], [repeat]])
    return keyboard


async def show_po(user_id, update: Update, page: int):
    try:
        po_order = orders_db.find(filter={'user_id': user_id})[page]
    except IndexError:
        await update.callback_query.answer(text='Вы ещё не сделали ни одного заказа, самое время начать)',
                                           show_alert=True)
        return
    order = po_order['order_items']
    cart = ''
    for resident in order.keys():
        for dish in order[resident].keys():
            if dish == 'status':
                continue
            cart += '{}: {} * {}\n'.format(dish, order[resident][dish]['quantity'], order[resident][dish]['price'])
    cart += 'Итого: {}р.'.format((po_order['total']))
    await update.callback_query.edit_message_text(text=cart)
    await update.callback_query.edit_message_reply_markup(po_inlinae(page, update.callback_query.from_user.id, order_num=po_order['order_num']))
    return


async def repeat_order(order_num, update: Update):
    rp_order = orders_db.find_one(filter={'order_num': order_num})
    order = rp_order['order_items']
    canceled_dishes = []
    for resident in order.keys():
        for dish in order[resident].keys():
            if dish == 'status':
                continue
            dish_info = get_one_dish(resident, dish)
            if not dish_info:
                canceled_dishes.append(dish)
            else:
                add_dish(user_id=rp_order['user_id'], resident=resident,
                         dish=dish, price=dish_info[0][3], amount=order[resident][dish]['quantity'])
    if not canceled_dishes:
        await update.callback_query.answer(text='Позиции успешно добавлены в вашу корзину',
                                     show_alert=True)
    else:
        msg = 'Следующие позиции в данный момент не доступны для заказа:\n'
        i = 1
        for d in canceled_dishes:
            msg += '{}.{}\n'.format(i, d)
            i += 1
        msg += 'Оставшиеся позиции успешно добавлены в корзину.'
        await update.callback_query.answer(text=msg, show_alert=True)
    return
