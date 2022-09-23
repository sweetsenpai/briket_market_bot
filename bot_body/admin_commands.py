from telegram import (ReplyKeyboardRemove,
                      Update,
                      ReplyKeyboardMarkup,
                      KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup)

from telegram.ext import (
    ContextTypes,
    ConversationHandler)
from briket_DB.config import mongodb
import logging
from briket_DB.residents import create, find_phone, delet_on_phone, read_all
admin = mongodb.admin
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

PHONE_AD_ADD, PHONE_RS_ADD = range(2)


async def add_new_admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text='Для добавления нового админа в базу пришли его номер телефона в формате:'
                                         '7XXXXXXXXXX')
    return PHONE_AD_ADD


async def add_new_admin_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text
    admin.insert_one({'phone': phone})
    await update.message.reply_text(text='Номер нового администратора({}) успешно добавлен, '
                                         'теперь админ может пройти регистрацию.'
                                         'Для прогождения регистрации необходимо написать в чат /reg_admin_start'.format(phone))
    return ConversationHandler.END


def del_resident_keyboard():
    buttons_res = []
    for resident in read_all():
        buttons_res.append(
            [
                InlineKeyboardButton(
                    text=resident['resident_name'],
                    callback_data=','.join(['del_resident', resident['resident_phone']])
                )
            ]
        )
    return InlineKeyboardMarkup(buttons_res)


async def del_resident(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_id = update.message.from_user.id

    if mongodb.admin.find_one({'chat_id': admin_id}) is None:
        await update.message.reply_text(text='Вы не являетесь администратором!')
        return
    else:
        await update.message.reply_text(
            text='Выберете резидента которого необходимо удалить:',
            reply_markup=del_resident_keyboard()
        )
        return


def del_admin_keyboard(admin_id: int):
    button_admin = []
    for admins in mongodb.admin.find({'chat_id': {'$ne': admin_id}}):
        button_admin.append(
            [
                InlineKeyboardButton(
                    text=admins['phone'],
                    callback_data=','.join(['del_admin', admins['phone']])
                )
            ]
        )
    return InlineKeyboardMarkup(button_admin)


async def dele_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_id = update.message.from_user.id

    if mongodb.admin.find_one({'chat_id': admin_id}) is None:
        await update.message.reply_text(text='Вы не являетесь администратором!')
        return
    else:
        await update.message.reply_text(
            text='Выберете номер администратора которого необходимо удалить из базы:',
            reply_markup=del_admin_keyboard(admin_id=admin_id)
        )
        return



async def add_new_resident_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text='Для добавления нового резидента в базу пришли его номер телефона в формате:'
                                         '7XXXXXXXXXX')
    return PHONE_AD_ADD


async def add_new_resident_end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text
    resident_new = {
        "resident_name": '',
        "chat_id": 123,
        "resident_addres": '',
        "resident_phone": phone,
        "resident_email": '',
        "description": '',
        "img_url": str('')}
    create(resident_new)
    await update.message.reply_text(text='Номер нового резидента({}) успешно добавлен!\n '
                                         'Теперь резидент может пройти регистрацию.\n'
                                         'Для прогождения регистрации необходимо написать в чат:\n /registration'.format(
        phone))
    return ConversationHandler.END





async def cancel_conv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text='Действие прервано!')
    return ConversationHandler.END


async def admin_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(''
                                    'Для добавления нового администратора воспользуйся коммандой:/add_new_admin \n'
                                    'Для удаления администратора воспользуйся коммандой:/del_admin\n'
                                    'Для добавления нового резидента воспользуйся коммандой:/add_new_resident\n'
                                    'Для удаления резидента воспользуйся коммандой:/del_resident\n'
                                    'Для простсмотра инструкции резидентов воспользуйся коммандой:/resident_info\n')
    return


async def resident_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Для добавления новых блюд или меню воспользуйся этой ссылкой:\n '
        'https://docs.google.com/spreadsheets/d/1p2sWvJQwo6oDxKP--PpJFiT_bhdGy9MjS4AulYCdHRo/edit?usp=sharing\n'
        'Если у вашего ресторана ещё нет своей странички меню, то добавьте её нажав на + в левом нижнем углу экрана.\n'
        'Дайте навзание новому листу так же, как вы указывали при регистрации в боте, соблюдая все регистры.\n'
        'После этого скопируете первые две строики из листа с названием "Пример".\n'
        'Теперь можно добавлять блюда по аналогии с шапкой таблицы.\n'
    )
    await update.message.reply_text(text=''
                                         'Если у вашего ресторана уже есть страничка с меню,\n'
                                         ' то прсто добавьте новое блюдо по аналогии.\n')
    await update.message.reply_text(text=''
                                         'ВАЖНО!!!!!\n'
                                         'При добавлении не целых чисел, указывайте дробную часть через точку "."\n'
                                         'В противном случае число будет отображаться не корректно.')
    return
