from telegram.ext import (ContextTypes)
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from bot_body.admin.access_level import admin_check, res_check
from briket_DB.sql_main_files.customers import find_id
from briket_DB.sql_main_files.workers import create


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.message.from_user.id
    customer = KeyboardButton(text='Клиент')
    admin = KeyboardButton(text='Администратор')
    resident = KeyboardButton(text='Резидент')
    a_keyboard = ReplyKeyboardMarkup(keyboard=[[customer], [admin], [resident]])
    print(context.args)
    if admin_check(chat) is True:
        await update.message.reply_text(text='Привет, выбери роль в меню ниже:', reply_markup=a_keyboard)
        return

    elif res_check(chat) is True:
        await update.message.reply_text(text='Привет')
        await resident_keyboard(update, context)
        return

    elif context.args[0] is not None:
        await update.message.reply_text(text='Привет, теперт ты будешь получать новые заказы.')
        create(update.message.chat_id, context.args[0])
        await worker_keyboard(update, context)
        return
    await customer_keyboard(update, context)
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
    await update.message.reply_text(text='Выбери действия в меню ниже', reply_markup=ad_functions)
    return


async def customer_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if find_id(update.message.from_user.id) is None:
        cust_func = ReplyKeyboardMarkup(
            [
                [KeyboardButton(text='Регистрация')],
                [KeyboardButton(text='Меню'), KeyboardButton(text='Оставить отзыв')],
                [KeyboardButton(text='FAQ'), KeyboardButton(text='Аккаунт')],
                [KeyboardButton(text='🛒Корзина🛒')]
            ], resize_keyboard=True, one_time_keyboard=False)
        hello_msg = '‎‎' \
                    '                           Привет, друг!\n\n' \
                    '                  Это Брикет Маркет Бот.\n\n' \
                    '  Я помогу тебе заказать любимые блюда у \n   резидентов фуд-корта «Брикет Маркет»\n\n\n' \
                    '                Нажми на кнопку «Регистрация»'
        await update.message.reply_text(text=hello_msg, reply_markup=cust_func)
        return
    else:
        cust_func = ReplyKeyboardMarkup(
            [
                [KeyboardButton(text='Меню'), KeyboardButton(text='Оставить отзыв')],
                [KeyboardButton(text='FAQ'), KeyboardButton(text='Аккаунт')],
                [KeyboardButton(text='🛒Корзина🛒')]
            ], resize_keyboard=True, one_time_keyboard=False)
    await update.message.reply_text(text='Выбери действия в меню ниже', reply_markup=cust_func)
    return


async def resident_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    res_func = ReplyKeyboardMarkup(
        [
            [KeyboardButton(text='FAQ рез.')],
            [KeyboardButton(text='Отчет')],
            [KeyboardButton(text='Новый резидент вход')],
            [KeyboardButton(text='Добавить нового сотрудника')]
        ], resize_keyboard=True, one_time_keyboard=False)
    await update.message.reply_text(text='Выбери действия в меню ниже', reply_markup=res_func)
    return


async def worker_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    res_func = ReplyKeyboardMarkup(
        [
            [KeyboardButton(text='FAQ рез.')]
        ], resize_keyboard=True, one_time_keyboard=False)
    await update.message.reply_text(text='Нажми на кнопку на клавиатуре, чтобы ознакомиться с FAQ', reply_markup=res_func)
    return


async def promo_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    res_func = ReplyKeyboardMarkup(
        [
            [KeyboardButton(text='Создать промокод')],
            [KeyboardButton(text='Активные промокоды')]
        ], resize_keyboard=True, one_time_keyboard=False)
    await update.message.reply_text(text='Выбери один из вариантов меню:', reply_markup=res_func)
    return


