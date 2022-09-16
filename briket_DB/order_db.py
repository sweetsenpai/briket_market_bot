from briket_DB.config import mongodb
from datetime import datetime
from briket_DB.residents import get_chat_id
from briket_DB.customers import find_user_by_id
from telegram.ext import ContextTypes
from telegram import (Update,
                      InlineKeyboardMarkup,
                      InlineKeyboardButton)
orders_db = mongodb.orders
sh_cart = mongodb.sh_cart


async def push_order(user_id: int, context: ContextTypes.DEFAULT_TYPE, receipt_type: str):
    cart = sh_cart.find_one({"user_id": user_id})
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    del cart['_id']
    cart['time'] = time
    cart['status'] = 'Новый'
    cart['order_num'] = datetime.now().microsecond
    cart['delivery_type'] = receipt_type
    orders_db.insert_one(cart)
#    sh_cart.delete_one({"user_id": user_id})
    await send_order_residents(cart['order_num'], context)
    return


def resident_inline_keyboard(order_num: int, resident: str) -> InlineKeyboardMarkup:
    order_num = str(order_num)
    accept = InlineKeyboardButton(text='Принять✅', callback_data=','.join(['accept', order_num, resident]))
    decline = InlineKeyboardButton(text='Отменить❌', callback_data=','.join(['decline_order', order_num, resident]))
    support = InlineKeyboardButton(text='Поддержка👨‍🔧', callback_data=','.join(['support', order_num, resident]))
    client = InlineKeyboardButton(text='Клиент📒', callback_data=','.join(['client', order_num, resident]))
    red = InlineKeyboardButton(text='Редактировать заказ⚙', callback_data=','.join(['redaction_order', order_num, resident]))
    rez = InlineKeyboardMarkup([[accept, decline], [support, client], [red]])
    return rez


async def send_order_residents(order_num: int, context: ContextTypes.DEFAULT_TYPE):
    full_order = orders_db.find_one({"order_num": order_num})
    for resident in full_order['order_items']:
        resident_order = 'Заказ №{}\nТип: {}\nСтатус: {}\n'.format(full_order['order_num'],
                                                                           full_order['delivery_type'], full_order['status'])
        for dish in full_order['order_items'][resident]:
            resident_order += '{}: {}\n'.format(dish, full_order['order_items'][resident][dish]['quantity'])
        await context.bot.sendMessage(text=resident_order,
                                      chat_id=get_chat_id(resident),
                                      reply_markup=resident_inline_keyboard(order_num, resident))
    return


async def accept_order(order_num: int, context: ContextTypes.DEFAULT_TYPE):
    order = orders_db.find_one({"order_num": order_num})


async def client_info(order_num: int, context: ContextTypes.DEFAULT_TYPE, msg_chat: int):
    order = orders_db.find_one({"order_num": order_num})
    user_id = order['user_id']
    user_name = (await context.bot.getChat(chat_id=user_id)).username
    phone = find_user_by_id(user_id)['phone']
    await context.bot.sendMessage(chat_id=msg_chat,
                                  text='Написать клиенту: @{}\n'
                                       'Позвонить клиенту: +{}'.format(user_name, phone))
    return


async def tech_support(context: ContextTypes.DEFAULT_TYPE, msg_chat: int):
    await context.bot.sendMessage(
        chat_id=msg_chat,
        text='Написать в тех.подждержку: @Sweet_Senpai'
    )
    return


async def order_status_up(order_num: int, update: Update):
    status = tuple(('Новый', 'Готовиться', 'Готов'))
    order = orders_db.find_one({"order_num": order_num})
    orders_db.find_one_and_update(filter=order, update={'$set': {"status": status[status.index(order['status']) + 1]}})
    for resident in order['order_items']:
        resident_order = 'Заказ №{}\nТип: {}\nСтатус: {}\n'.format(order['order_num'],
                                                                           order['delivery_type'], order['status'])
        await update.callback_query.edit_message_text(text=resident_order,
                                                      reply_markup=resident_inline_keyboard(order_num=order_num,
                                                                                            resident=resident))

