import asyncio

import telegram.error

from briket_DB.config import mongodb
from datetime import datetime
from briket_DB.sql_main_files.residents import get_chat_id
from briket_DB.sql_main_files.customers import find_user_by_id
from telegram.ext import ContextTypes
from briket_DB.shopping.shcart_db import show_cart
from telegram import (Update,
                      InlineKeyboardMarkup,
                      InlineKeyboardButton)
from briket_DB.shopping.promotions import apply_promo
from delivery.yandex_api import send_delivery_order
orders_db = mongodb.orders
sh_cart = mongodb.sh_cart
admin = mongodb.admin


async def push_order(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    cart = sh_cart.find_one({"user_id": user_id})
    try:
        del cart['_id']
    except TypeError:
        await context.bot.sendMessage(chat_id=user_id, text='Нельзя оформить заказ, в корзине ничего нет.')
        return
    cart['time'] = datetime.now()
    for resident in cart['order_items']:
        cart['order_items'][resident]['status'] = 'Новый'
    if cart['delivery_type'] == 'Доставка':
        cart['delivery']['id'] = send_delivery_order(order=cart)
        if cart['delivery']['id'] is False:
            await context.bot.sendMessage(chat_id=user_id, text='Во время оформления доставки произошла ошибка.\n'
                                                                'Оформление заказа прервано!\n'
                                                                'Свяжитесь с поддержкой!')
            return

    orders_db.insert_one(cart)
    await send_order_residents(cart['order_num'], context)

    msg = 'Номер вашего заказа №{}\n' \
          '{}\n\n' \
          'Вы получите оповещение, когда ваш заказ будет готов к выдаче!'.format(cart['order_num'], show_cart(user_id=user_id))
    await context.bot.sendMessage(chat_id=user_id, text=msg)
    sh_cart.delete_one({"user_id": user_id})
    return


def resident_inline_keyboard(order_num: int, resident: str, btn_text='✅', cbd='accept') :
    order_num = str(order_num)
    accept = InlineKeyboardButton(text=btn_text, callback_data=','.join([cbd, order_num, resident]))
    decline = InlineKeyboardButton(text='Отменить❌', callback_data=','.join(['decline_order', order_num, resident]))
    support = InlineKeyboardButton(text='Поддержка👨‍🔧', callback_data=','.join(['support', order_num, resident]))
    client = InlineKeyboardButton(text='Клиент📒', callback_data=','.join(['client', order_num, resident]))
#   red = InlineKeyboardButton(text='Редактировать заказ⚙', callback_data=','.join(['redaction_order',
    #   order_num, resident]))
    rez = InlineKeyboardMarkup([[accept], [support]])
    admin_board = InlineKeyboardMarkup([[decline], [client]])
    return rez, admin_board


async def send_order_residents(order_num: int, context: ContextTypes.DEFAULT_TYPE):
    full_order = orders_db.find_one({"order_num": order_num})
    for resident in full_order['order_items']:
        try:
            resident_order = 'Заказ №{}\nТип: {}\nСтатус: ' ' Новый📨\n Адрес:{}\n'.format(full_order['order_num'],
                                                                                full_order['delivery_type'],
                                                                                full_order['delivery']['addres'])
        except KeyError:
            resident_order = 'Заказ №{}\nТип: {}\nСтатус: ' ' Новый📨\n'.format(full_order['order_num'],
                                                                                         full_order['delivery_type'])
        for count, dish in enumerate(full_order['order_items'][resident]):
            try:
                resident_order += '{}. {}: {} шт. \n'.format(count + 1, dish,
                                                             full_order['order_items'][resident][dish]['quantity'])
            except TypeError:
                pass
        resident_order += '\n Клиент: {}'.format(find_user_by_id(full_order['user_id'])['name'])
        await context.bot.sendMessage(text=resident_order,
                                      chat_id=get_chat_id(resident),
                                      reply_markup=resident_inline_keyboard(order_num, resident=resident)[0])
        for admins in admin.find():
            try:
                await context.bot.sendMessage(text=resident_order,
                                              chat_id=admins['chat_id'], reply_markup=resident_inline_keyboard(order_num, resident=resident)[1])
            except telegram.error.BadRequest or KeyError:
                pass
    return


async def accept_order(order_num: int, update: Update, resident: str):
    full_order = orders_db.find_one({"order_num": order_num})
    orders_db.find_one_and_update(filter=full_order,
                                  update={'$set': {"order_items.{}.status".format(resident): 'Готовится'}})
    try:
        messeg = 'Заказ №{}\nТип: {}\nСтатус:  Готовится👨‍🍳\nАдрес:{}\n'.format(full_order['order_num'],
                                                                                  full_order['delivery_type'],
                                                                                  full_order['delivery']['addres'])
    except KeyError:
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
                                                                                        cbd='finish_order')[0])


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
        if full_order['delivery_type'] == 'Доставка':
            await context.bot.sendMessage(
                chat_id=full_order['user_id'],
                text='Ваш заказ №{}\n'
                     'Передан в доставку!🎉🎉🎉'.format(full_order['order_num'])
            )
        elif full_order['delivery_type'] == 'Самовывоз':
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




