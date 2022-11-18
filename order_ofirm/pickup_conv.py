from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler, MessageHandler, CommandHandler, filters)
from briket_DB.order_db import push_order
from briket_DB.promotions import chek_promo, add_promo_cart

ONE, TWO = range(2)


async def first_pickup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    button1 = KeyboardButton(text='Да')
    button2 = KeyboardButton(text='Нет')
    key = ReplyKeyboardMarkup(keyboard=[[button1], [button2]])
    await update.message.reply_text(text='Хотите активировать промокод?\n'
                                         'Чтобы остановить оформление заказа нажмите-> /stop', reply_markup=key)
    return


async def second_pickup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answer = update.message
    if answer.text == 'Нет':
        await push_order(user_id=answer.from_user.id, context=context, receipt_type='Самовывоз', update=update)
        return ConversationHandler.END
    elif answer.text == 'Да':
        await update.message.reply_text(text='Введите промокод')
        return ONE
    await push_order(user_id=answer.from_user.id, context=context, receipt_type='Самовывоз', update=update)
    return ConversationHandler.END


async def finish_pickup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answer = update.message
    promo_result = chek_promo(promo_code=answer.text, user_id=answer.from_user.id)
    if promo_result[1] is False:
        await answer.reply_text(text=promo_result[0])
        await first_pickup(update, context)
        return ONE

    await answer.reply_text(text=promo_result[0])
    await push_order(user_id=answer.from_user.id, context=context, receipt_type='Самовывоз', update=update)
    return ConversationHandler.END


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text='Оформление закза прервана')
    return ConversationHandler.END

pickup_conversation = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex('Самовывоз'), finish_pickup)],
    states={
        ONE: [MessageHandler(filters.TEXT, second_pickup)],
    },
    fallbacks=[CommandHandler('stop', stop)])
