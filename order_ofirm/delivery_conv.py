from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler, MessageHandler, CommandHandler, filters)
from briket_DB.order_db import push_order
from briket_DB.promotions import chek_promo
from delivery.yandex_api import delivery_range
ONE, TWO, THREE = range(3)


async def first_delivery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text='Укажите адрес доставки')
    return ONE


async def second_delivery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    addres = update.message.text
    chek = delivery_range(addres)
    if chek[0] is True:
        button1 = KeyboardButton(text='Да')
        button2 = KeyboardButton(text='Нет')
        key = ReplyKeyboardMarkup(keyboard=[[button1], [button2]])
        await update.message.reply_text(text='У вас есть промокод?', reply_markup=key)
        return TWO
    elif chek[0] is False:
        await update.message.reply_text(text=chek[1])
        await update.message.reply_text(text='Вы можете указать другой адрес доставки '
                                             'или прервать оформление командой /stop')
        return ONE


async def third_delivery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answer = update.message
    if answer.text == 'Нет':
        await push_order(user_id=answer.from_user.id, context=context, receipt_type='Самовывоз', update=update)
        return ConversationHandler.END
    elif answer.text == 'Да':
        await update.message.reply_text(text='Введите промокод')
        return TWO


async def finish_delivery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answer = update.message
    promo_result = chek_promo(promo_code=answer.text, user_id=answer.from_user.id)
    if promo_result[1] is False:
        await answer.reply_text(text=promo_result[0])
        await third_delivery(update, context)
        return ONE

    await answer.reply_text(text=promo_result[0])
    await push_order(user_id=answer.from_user.id, context=context, receipt_type='Доставка', update=update)
    return ConversationHandler.END

