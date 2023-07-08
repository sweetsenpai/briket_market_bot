from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ContextTypes,
    ConversationHandler, MessageHandler, CommandHandler, filters)
from payments.ykassa_integration import create_payment
from briket_DB.shopping.promotions import chek_promo
from briket_DB.sql_main_files.customers import read_one
from bot_body.functional_key import start
from datetime import datetime

ONE, TWO = range(2)


async def first_pickup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if read_one(update.message.from_user.id) is False:
        await update.message.reply_text(text='Для оформления заказа необходимо пройти регистрацию.\n'
                                                'Это займет всего пару минут.')
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
    button1 = KeyboardButton(text='Да')
    button2 = KeyboardButton(text='Нет')
    key = ReplyKeyboardMarkup(keyboard=[[button1], [button2]])
    await update.message.reply_text(text='Хотите активировать промокод?\n'
                                         'Чтобы остановить оформление заказа нажмите-> /stop', reply_markup=key)
    return ONE


async def second_pickup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answer = update.message
    if answer.text.lower() == 'нет':
        await create_payment(user_id=answer.from_user.id, delivery_type='Самовывоз', update=update)
        return ConversationHandler.END
    elif answer.text.lower() == 'да':
        await update.message.reply_text(text='Введите промокод')
        return TWO
    elif answer.text == '/stop':
        await stop(update, context)
        return ConversationHandler.END
    else:
        await update.message.reply_text(text='Не совсем тебя понял(\n Воспользуйся клавиатурой или просто напиши Да/Нет')
        return ONE


async def finish_pickup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answer = update.message
    if answer.text == '/stop':
        await stop(update, context)
        return ConversationHandler.END

    promo_result = chek_promo(promo_code=answer.text, user_id=answer.from_user.id)
    if promo_result[1] is False:
        await answer.reply_text(text=promo_result[0])
        await first_pickup(update, context)
        return ONE

    await answer.reply_text(text=promo_result[0])
    await create_payment(user_id=answer.from_user.id, delivery_type='Самовывоз', update=update)
    await start(update, context)
    return ConversationHandler.END


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text="Заказ отменен :( \nХочешь выбрать что-то другое?»")
    await start(update, context)
    return ConversationHandler.END

pickup_conversation = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex('Самовывоз'), first_pickup)],
    states={
        ONE: [MessageHandler(filters.TEXT, second_pickup)],
        TWO: [MessageHandler(filters.TEXT, finish_pickup)]
    },
    fallbacks=[CommandHandler('stop', stop)], conversation_timeout=300)
