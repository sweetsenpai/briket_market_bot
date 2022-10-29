from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters, ContextTypes)
from telegram import (
                      Update,
                      ReplyKeyboardMarkup,
                      KeyboardButton)
import re
from briket_DB.promotions import start_sale, sales_db
CODE, TEXT, ONE_TIME, START_PRICE, PROCENT = range(5)


async def add_promo_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text='Пожалуйста введите кодовое слово или фразу которая будет использоваться.')
    return CODE


async def add_promo_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code_word = update.message.text
    start_sale(promo_code=code_word)
    sales_db.find_one_and_update(filter={'code': code_word}, update={'$set': {'master': update.message.chat_id}})
    await update.message.reply_text(text='Введите описание акции, которое увидят пользователи.')
    return TEXT


async def add_promo_onetime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    promo_text = update.message.text
    sales_db.find_one_and_update(filter={'master': update.message.chat_id}, update={'$set': {'text': promo_text}})
    keyboard_onetime = ReplyKeyboardMarkup(keyboard=[[
        KeyboardButton(text='Да'), KeyboardButton(text='Нет')
    ]], one_time_keyboard=True)
    await update.message.reply_text(text='Сделать промокод однаразовым ?', reply_markup=keyboard_onetime)
    return ONE_TIME


async def add_promo_start_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == 'Да':
        sales_db.find_one_and_update(filter={'master': update.message.chat_id}, update={'$set': {'one_time': True}})
    keyboard_onetime = ReplyKeyboardMarkup(keyboard=[[ KeyboardButton(text='Нет')]], one_time_keyboard=True)
    await update.message.reply_text(text='Установить сумму от которой будет действовать промокод?\n'
                                         'Если да, то просто введите желаеммую сумму, в противном случае нажмите <<нет>> на клавиатуре',
                                    reply_markup=keyboard_onetime)
    return START_PRICE


async def add_promo_procent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_price = update.message.text
    pure_price = str(re.findall(pattern='[0-9]+', string=start_price)[0])
    print(start_price)
    if start_price != 'Нет':
        sales_db.find_one_and_update(filter={'master': update.message.chat_id},
                                     update={'$set': {'start_price': round(float(pure_price), 2)}})

    await update.message.reply_text(text='Установите значение промокода.\n'
                                         'Если скида это фиксированная сумма, то просто введите сумму.\n'
                                         'Если скидка это процент, то просто укажите процент скидки <<XX%>>.')
    return PROCENT


async def add_promo_end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    promo_procent = update.message.text
    pure_d = str(re.findall(pattern='[0-9]+', string=promo_procent)[0])
    if promo_procent[-1] == '%':
        sales_db.find_one_and_update(filter={'master': update.message.chat_id},
                                     update={'$set': {'procent': round(float(pure_d), 2)}})
    else:
        sales_db.find_one_and_update(filter={'master': update.message.chat_id},
                                     update={'$set': {'ammount': round(float(pure_d), 2)}})
    sales_db.find_one_and_update(filter={'master': update.message.chat_id},
                                 update={'$unset': {'master': ''}})
    await update.message.reply_text(text='Промокод успешно создан!')
    return ConversationHandler.END


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text='Регистрация прервана')
    return ConversationHandler.END

