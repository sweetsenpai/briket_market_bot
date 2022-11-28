from telegram.ext import (
    ConversationHandler,
    ContextTypes)
import asyncio
from briket_DB.sql_main_files.customers import read_all
from telegram import (
                      Update,
                      ReplyKeyboardMarkup,
                      KeyboardButton)
import re
from briket_DB.shopping.promotions import start_sale, sales_db
from text_integration.pastebin_integration import get_text_api
CODE, TEXT, ONE_TIME, START_PRICE, PROCENT, START_DISTRIBUTION = range(6)


async def add_promo_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text=get_text_api('1Ct6yG2P'))
    return CODE


async def add_promo_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code_word = update.message.text
    start_sale(promo_code=code_word, master=update.message.chat_id)
    await update.message.reply_text(text=get_text_api('VgUzQXWc'))
    return TEXT


async def add_promo_onetime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    promo_text = update.message.text
    sales_db.find_one_and_update(filter={'master': update.message.chat_id}, update={'$set': {'description': promo_text}})
    keyboard_onetime = ReplyKeyboardMarkup(keyboard=[[
        KeyboardButton(text='Да'), KeyboardButton(text='Нет')
    ]], one_time_keyboard=True)
    await update.message.reply_text(text=get_text_api('69Z5W6T5'), reply_markup=keyboard_onetime)
    return ONE_TIME


async def add_promo_start_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == 'Да':
        sales_db.find_one_and_update(filter={'master': update.message.chat_id}, update={'$set': {'one_time': True}})
    keyboard_onetime = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Нет')]], one_time_keyboard=True)
    await update.message.reply_text(text=get_text_api('pSnmnMhn'),
                                    reply_markup=keyboard_onetime)
    return START_PRICE


async def add_promo_procent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_price = update.message.text
    if start_price != 'Нет':
        pure_price = str(re.findall(pattern='[0-9]+', string=start_price)[0])
        sales_db.find_one_and_update(filter={'master': update.message.chat_id},
                                     update={'$set': {'start_price': round(float(pure_price), 2)}})

    await update.message.reply_text(text=get_text_api('C5JG3ZdN'))
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
    await update.message.reply_text(text='Промокод успешно создан!')
    await update.message.reply_text(text='Начать рассылку?',
                                    reply_markup=ReplyKeyboardMarkup([[KeyboardButton('Да'), KeyboardButton('Нет')]]))
    return START_DISTRIBUTION


async def promo_distribution(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answer = update.message.text
    text_prm = sales_db.find_one(filter={'master': update.message.chat_id})['description']
    sales_db.find_one_and_update(filter={'master': update.message.chat_id},
                                 update={'$unset': {'master': ''}})['description']
    print(text_prm)
    if answer == 'Да':
        await update.message.reply_text('Рассылка запущена!')
        context.application.create_task(
            asyncio.gather(
                *(
                    context.bot.send_message(
                        chat_id=customer['chat_id'],
                        text=text_prm
                    )
                    for customer in read_all()
                ), return_exceptions=True
            )
        )
        await update.message.reply_text('Рассылка завершена!')
    await update.message.reply_text('Создание промокода завершено!')
    return ConversationHandler.END


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text='Создание прервано')
    return ConversationHandler.END

