from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram.ext import (
    ContextTypes,
    ConversationHandler, MessageHandler, CommandHandler, filters)
from payments.ykassa_integration import create_payment
from briket_DB.shopping.promotions import chek_promo
from delivery.yandex_api import delivery_range
from briket_DB.shopping.shcart_db import sh_cart
from briket_DB.sql_main_files.customers import read_one
from briket_DB.sql_main_files.customers import addres_keyboard
from bot_body.functional_key import start
from datetime import datetime
ONE, TWO, THREE, FOUR = range(4)


def addres_keyboard_del(user_id):
    key = []
    for a in addres_keyboard(user_id):
        key.append(
            [KeyboardButton(text=a)]
        )
    return ReplyKeyboardMarkup(key)


async def first_delivery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if read_one(update.message.from_user.id) is False:
        await update.message.reply_text(text='Для оформления заказа необходимо пройти регистрацию.\n'
                                                'Это займет всего пару минут.')
        await start(update, context)
        return ConversationHandler.END

    if datetime.now().weekday() == 6:
        if int(datetime.now().hour) >= 23 or int(datetime.now().hour) < 11:
            await update.message.reply_text(text='График работы\n'
                                                    'Пн-Сб: с 10:00 до 22:00\n'
                                                    'Вск: c 11:00 до 23:00')
            await start(update, context)
            return ConversationHandler.END

    else:
        if int(datetime.now().hour) >= 21 or int(datetime.now().hour) < 10:
            await update.message.reply_text(text='График работы\n'
                                                    'Пн-Сб: с 10:00 до 22:00\n'
                                                    'Вск: c 11:00 до 23:00')
            await start(update, context)
            return ConversationHandler.END

    await update.message.reply_text(text='Укажите адрес доставки',
                                    reply_markup=addres_keyboard_del(
                                        update.message.from_user.id
                                    ))
    return ONE


async def second_delivery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    addres = update.message.text
    chek = delivery_range(addres)
    if addres == '/cancel':
        await stop(update, context)
        return ConversationHandler.END

    if chek[0] is True:
        sh_cart.find_one_and_update(filter={'user_id': update.message.from_user.id},
                                    update={'$set': {"delivery.addres": addres}})
        button1 = KeyboardButton(text='Нет')
        button2 = KeyboardButton(text='Назад')
        key = ReplyKeyboardMarkup(keyboard=[[button1], [button2]])
        await update.message.reply_text(text='Отлично, ты указал корректный адрес.')

        await update.message.reply_text(text='Хочешь добавить комментарий для курьера?\n'
                                             'Если тебя легко найти, то просто нажми <Нет> на клавиатуре',
                                        reply_markup=key)
        await update.message.reply_text(text='Всегда можно нажать "Назад", чтобы вернуться на предыдущий шаг.')
        return TWO
    elif chek[0] is False:
        await update.message.reply_text(text=chek[1])
        await update.message.reply_text(text='Прости, твой адрес находится вне зоны доставки. \n'
                                             'Выбери другой адрес или отмени оформление заказа /cancel')
        return ONE


async def comments_delivery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answer = update.message.text
    if answer == '/cancel':
        await stop(update, context)
        return ConversationHandler.END
    elif answer == 'Назад':
        await update.message.reply_text(text='Укажи адрес доставки',
                                        reply_markup=addres_keyboard_del(
                                            update.message.from_user.id
                                        ))
        return ONE
    elif sh_cart.find_one(filter={'user_id': update.message.from_user.id, 'delivery.comment': {"$exists": True}}) is None:
        sh_cart.find_one_and_update(filter={'user_id': update.message.from_user.id},
                                    update={'$set': {"delivery.comment": answer}})
    button1 = KeyboardButton(text='Да')
    button2 = KeyboardButton(text='Нет')
    button3 = KeyboardButton(text='Назад')
    key = ReplyKeyboardMarkup(keyboard=[[button1], [button2], [button3]])
    await update.message.reply_text(text='Хотите активировать промокод?\n', reply_markup=key)
    return THREE


async def promo_delivery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answer = update.message
    if answer.text == '/cancel':
        await stop(update, context)
        return ConversationHandler.END
    elif answer.text == 'Назад':
        button1 = KeyboardButton(text='Нет')
        button2 = KeyboardButton(text='Назад')
        key = ReplyKeyboardMarkup(keyboard=[[button1], [button2]])
        await update.message.reply_text(text='Хочешь добавить комментарий для курьера?\n'
                                             'Если тебя легко найти, то просто нажми <Нет> на клавиатуре',
                                        reply_markup=key)
        return TWO
    elif answer.text.lower() == 'нет':
        await create_payment(user_id=answer.from_user.id, delivery_type='Доставка', update=update)
        return ConversationHandler.END
    elif answer.text.lower() == 'да':
        await update.message.reply_text(text='Введи промокод')
        return FOUR
    else:
        await update.message.reply_text(text='Не совсем тебя понял(\n Воспользуйся клавиатурой или просто напиши Да/Нет')
        return TWO


async def finish_delivery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answer = update.message
    if answer.text == '/cancel':
        await stop(update, context)
        return ConversationHandler.END
    elif answer.text == 'Назад':
        button1 = KeyboardButton(text='Да')
        button2 = KeyboardButton(text='Нет')
        button3 = KeyboardButton(text='Назад')
        key = ReplyKeyboardMarkup(keyboard=[[button1], [button2], [button3]], one_time_keyboard=True)
        await update.message.reply_text(text='Хотите активировать промокод?\n', reply_markup=key)
        return THREE
    promo_result = chek_promo(promo_code=answer.text, user_id=answer.from_user.id)
    if promo_result[1] is False:
        await answer.reply_text(text=promo_result[0])
        await promo_delivery(update, context)
        return TWO
    cust_func = ReplyKeyboardMarkup(
        [
            [KeyboardButton(text='Меню'), KeyboardButton(text='Оставить отзыв')],
            [KeyboardButton(text='FAQ'), KeyboardButton(text='Аккаунт')],
            [KeyboardButton(text='🛒Корзина🛒')]
        ], resize_keyboard=True, one_time_keyboard=False)
    await answer.reply_text(text=promo_result[0], reply_markup=cust_func)
    await create_payment(user_id=answer.from_user.id, delivery_type='Доставка', update=update)
    return ConversationHandler.END


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Заказ отменен :( \nХочешь выбрать что-то другое?»", reply_markup=ReplyKeyboardRemove()
    )
    await start(update, context)
    return ConversationHandler.END

del_conv = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex('Доставка'), first_delivery)],
    states={
        ONE: [MessageHandler(filters.Regex('[а-яА-ЯёЁ]'), second_delivery)],
        TWO: [MessageHandler(filters.TEXT, comments_delivery)],
        THREE: [MessageHandler(filters.TEXT, promo_delivery)],
        FOUR: [MessageHandler(filters.TEXT, finish_delivery)],
    },
    fallbacks=[CommandHandler('cancel', stop)], conversation_timeout=300)
