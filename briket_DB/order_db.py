from briket_DB.config import mongodb
from datetime import datetime
from briket_DB.residents import get_chat_id
from briket_DB.customers import find_user_by_id
from telegram.ext import ContextTypes
from briket_DB.shcart_db import show_cart
from telegram import (Update,
                      InlineKeyboardMarkup,
                      InlineKeyboardButton)
orders_db = mongodb.orders
sh_cart = mongodb.sh_cart
admin = mongodb.admin


async def push_order(user_id: int, context: ContextTypes.DEFAULT_TYPE, receipt_type: str, update: Update):
    cart = sh_cart.find_one({"user_id": user_id})
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    del cart['_id']
    cart['time'] = time
    cart['order_num'] = datetime.now().microsecond
    cart['delivery_type'] = receipt_type
    for resident in cart['order_items']:
        cart['order_items'][resident]['status'] = 'Новый'
    orders_db.insert_one(cart)
    await send_order_residents(cart['order_num'], context)
    msg = 'Номер вашего заказа №{}\n' \
          '{}\n\n' \
          'Вы получите оповещение, когда ваш заказ будет готов к выдаче!'.format(cart['order_num'],
                                                                                show_cart(user_id=user_id))
    await update.callback_query.edit_message_text(
        text=msg
    )
    sh_cart.delete_one({"user_id": user_id})
    return


def resident_inline_keyboard(order_num: int, resident: str, btn_text='✅', cbd='accept') -> InlineKeyboardMarkup:
    order_num = str(order_num)
    accept = InlineKeyboardButton(text=btn_text, callback_data=','.join([cbd, order_num, resident]))
    decline = InlineKeyboardButton(text='Отменить❌', callback_data=','.join(['decline_order', order_num, resident]))
    support = InlineKeyboardButton(text='Поддержка👨‍🔧', callback_data=','.join(['support', order_num, resident]))
    client = InlineKeyboardButton(text='Клиент📒', callback_data=','.join(['client', order_num, resident]))
#   red = InlineKeyboardButton(text='Редактировать заказ⚙', callback_data=','.join(['redaction_order',
    #   order_num, resident]))
    rez = InlineKeyboardMarkup([[accept, decline], [support, client]])
    return rez


async def send_order_residents(order_num: int, context: ContextTypes.DEFAULT_TYPE):
    full_order = orders_db.find_one({"order_num": order_num})
    for resident in full_order['order_items']:
        resident_order = 'Заказ №{}\nТип: {}\nСтатус: ' ' Новый📨\n'.format(full_order['order_num'],
                                                                            full_order['delivery_type'])
        for count, dish in enumerate(full_order['order_items'][resident]):
            try:
                resident_order += '{}. {}: {} шт. \n'.format(count + 1, dish,
                                                             full_order['order_items'][resident][dish]['quantity'])
            except TypeError: pass
        await context.bot.sendMessage(text=resident_order,
                                      chat_id=get_chat_id(resident),
                                      reply_markup=resident_inline_keyboard(order_num, resident=resident))
        for admins in admin.find():
            try:
                await context.bot.sendMessage(text=resident_order,
                                              chat_id=admins['chat_id'])
            except KeyError: pass
    return


async def accept_order(order_num: int, update: Update, resident: str):
    full_order = orders_db.find_one({"order_num": order_num})
    orders_db.find_one_and_update(filter=full_order,
                                  update={'$set': {"order_items.{}.status".format(resident): 'Готовится'}})

    messeg = 'Заказ №{}\nТип: {}\nСтатус:  Готовится👨‍🍳\n'.format(full_order['order_num'],
                                                                   full_order['delivery_type'])
    for count, dish in enumerate(full_order['order_items'][resident]):
        try:
            messeg += '{}. {}: {} шт. \n'.format(count + 1, dish, full_order['order_items'][resident][dish]['quantity'])
        except TypeError: pass
    await update.callback_query.edit_message_text(text=messeg,
                                                  reply_markup=resident_inline_keyboard(order_num=order_num,
                                                                                        resident=resident,
                                                                                        btn_text='Готов🏆',
                                                                                        cbd='finish_order'))


async def finish_order(order_num: int, update: Update, resident: str, context: ContextTypes.DEFAULT_TYPE):
    full_order = orders_db.find_one({"order_num": order_num})
    orders_db.find_one_and_update(filter=full_order,
                                  update={'$set': {"order_items.{}.status".format(resident): 'Готов'}})
    order_statuses = orders_db.find_one({"order_num": order_num})['order_items']
    chek_order = 0
    for status in order_statuses:
        if order_statuses[status]['status'] == 'Готов':
            chek_order += 1
    if chek_order == len(order_statuses):
        await context.bot.sendMessage(
            chat_id=full_order['user_id'],
            text='Ваш заказ №{}\n'
                 'Готов к выдаче!🎉🎉🎉'.format(full_order['order_num'])
        )
        orders_db.find_one_and_update(filter=full_order,
                                      update={'$set': {'Сompleted': True}})
        for admins in admin.find():
            try:
                await context.bot.sendMessage(
                    chat_id=admins['chat_id'],
                    text='Заказ №{}\n'
                     'Готов к выдаче!🎉🎉🎉'.format(full_order['order_num'])
                )
            except KeyError: pass
    messeg = 'Заказ №{}\nТип: {}\nСтатус:  Готов🏆\n'.format(full_order['order_num'],
                                                                    full_order['delivery_type'])

    for count, dish in enumerate(full_order['order_items'][resident]):
        try:
            messeg += '{}. {}: {} шт. \n'.format(count + 1, dish, full_order['order_items'][resident][dish]['quantity'])
        except TypeError:
            pass
    await update.callback_query.edit_message_text(text=messeg, reply_markup=None)


async def decline_order(order_num: int, update: Update, resident: str):
    full_order = orders_db.find_one({"order_num": order_num})
    orders_db.find_one_and_update(filter=full_order,
                                  update={'$set': {"order_items.{}.status".format(resident): 'Отменен'}})
    messeg = 'Заказ №{}\nТип: {}\nСтатус:  Отменен❌\n'.format(full_order['order_num'],
                                                                    full_order['delivery_type'])
    await update.callback_query.edit_message_text(text=messeg)


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

