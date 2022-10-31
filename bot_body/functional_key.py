from telegram.ext import (ContextTypes)
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    customer = KeyboardButton(text='Клиент')
    admin = KeyboardButton(text='Администратор')
    resident = KeyboardButton(text='Резидент')
    role_keyboard = ReplyKeyboardMarkup(keyboard=[[customer], [admin], [resident]])
    await update.message.reply_text(text='Привет, выбери роль в меню ниже:', reply_markup=role_keyboard)
    return


async def admin_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ad_functions = ReplyKeyboardMarkup(
        [
            [KeyboardButton(text='Добавить админ.'),
             KeyboardButton(text='Удалить админ.')],
            [KeyboardButton(text='Добавить резидента'),
             KeyboardButton(text='Удалить резидента')],
            [KeyboardButton(text='FAQ админ.'),
             KeyboardButton(text='FAQ рез.')],
            [KeyboardButton(text='Отчет'),
             KeyboardButton(text='Новый админ. вход')],
            [KeyboardButton(text='Промокоды'), KeyboardButton(text='Создать рассылку')]
        ], resize_keyboard=True, one_time_keyboard=False)
    await update.message.reply_text(text='Выбири действия в меню ниже', reply_markup=ad_functions)
    return


async def customer_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cust_func = ReplyKeyboardMarkup(
        [
            [KeyboardButton(text='Регистрация')],
            [KeyboardButton(text='Меню')],
            [KeyboardButton(text='FAQ')],
            [KeyboardButton(text='Аккаунт')],
            [KeyboardButton(text='Активировать промокод')]
        ], resize_keyboard=True, one_time_keyboard=False)
    await update.message.reply_text(text='Выбири действия в меню ниже', reply_markup=cust_func)
    return


async def resident_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    res_func = ReplyKeyboardMarkup(
        [
            [KeyboardButton(text='FAQ рез.')],
            [KeyboardButton(text='Отчет')],
            [KeyboardButton(text='Новый резидент вход')]
        ], resize_keyboard=True, one_time_keyboard=False)
    await update.message.reply_text(text='Выбири действия в меню ниже', reply_markup=res_func)
    return


async def promo_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    res_func = ReplyKeyboardMarkup(
        [
            [KeyboardButton(text='Создать промокод')],
            [KeyboardButton(text='Активные промокоды')]
        ], resize_keyboard=True, one_time_keyboard=False)
    await update.message.reply_text(text='Выбири один из вариантов меню:', reply_markup=res_func)
    return