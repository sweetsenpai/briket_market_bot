from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler, MessageHandler, CommandHandler, filters)
from briket_DB.order_db import push_order
from briket_DB.promotions import chek_promo
from delivery.yandex_api import delivery_range
from order_ofirm.pickup_conv import stop
from briket_DB.shcart_db import sh_cart

ONE, TWO, THREE, FOUR = range(4)


async def first_delivery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text='Укажите адрес доставки')
    return ONE


async def second_delivery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    addres = update.message.text
    chek = delivery_range(addres)
    if chek[0] is True:
        sh_cart.find_one_and_update(filter={'user_id': update.message.from_user.id},
                                    update={'$set': {"delivery.addres": addres}})
        button1 = KeyboardButton(text='Нет')
        key = ReplyKeyboardMarkup(keyboard=[[button1]])
        await update.message.reply_text(text='Отлично, вы указали корректный адрес.')

        await update.message.reply_text(text='Хотите добавить комментарии для курьера?\n'
                                             'Если вас легко найти, то просто нажмите <Нет> на клавиатуре',
                                        reply_markup=key)
        return TWO
    elif chek[0] is False:
        await update.message.reply_text(text=chek[1])
        await update.message.reply_text(text='Вы можете указать другой адрес доставки '
                                             'или прервать оформление командой /stop')
        return ONE


async def comments_delivery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answer = update.message.text
    if sh_cart.find_one(filter={'user_id': update.message.from_user.id, 'delivery.comment': {"$exists": True}}) is None:
        sh_cart.find_one_and_update(filter={'user_id': update.message.from_user.id},
                                    update={'$set': {"delivery.comment": answer}})
    button1 = KeyboardButton(text='Да')
    button2 = KeyboardButton(text='Нет')
    key = ReplyKeyboardMarkup(keyboard=[[button1], [button2]])
    await update.message.reply_text(text='Хотите активировать промокод?\n', reply_markup=key)
    return THREE


async def promo_delivery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answer = update.message
    if answer.text == 'Нет':
        await push_order(user_id=answer.from_user.id, context=context, receipt_type='Доставка', update=update)
        return ConversationHandler.END
    elif answer.text == 'Да':
        await update.message.reply_text(text='Введите промокод')
        return FOUR


async def finish_delivery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answer = update.message
    promo_result = chek_promo(promo_code=answer.text, user_id=answer.from_user.id)
    if promo_result[1] is False:
        await answer.reply_text(text=promo_result[0])
        await promo_delivery(update, context)
        return TWO

    await answer.reply_text(text=promo_result[0])
    await push_order(user_id=answer.from_user.id, context=context, receipt_type='Доставка', update=update)
    return ConversationHandler.END


del_conv = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex('Доставка'), first_delivery)],
    states={
        ONE: [MessageHandler(filters.TEXT, second_delivery)],
        TWO: [MessageHandler(filters.TEXT, comments_delivery)],
        THREE: [MessageHandler(filters.TEXT, promo_delivery)],
        FOUR: [MessageHandler(filters.TEXT, finish_delivery)],
    },
    fallbacks=[CommandHandler('stop', stop)]
)