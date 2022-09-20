from telegram import (ReplyKeyboardRemove,
                      Update,
                      ReplyKeyboardMarkup,
                      KeyboardButton)

from telegram.ext import (
    ContextTypes,
    ConversationHandler)
from briket_DB.config import mongodb
import logging
from briket_DB.residents import create, find_phone, delet_on_phone
admin = mongodb.admin
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

PHONE_AD_ADD, PHONE_AD_DEL, PHONE_RS_ADD, PHONE_RS_DEL = range(4)


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


async def dele_admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text='Для удаления администратора из базы напиши его номер в форматье:'
                                         '7XXXXXXXXXX')
    return PHONE_AD_DEL


async def del_admin_end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.contact.phone_number
    if admin.find_one({'phone': phone}) is not None:
        await update.message.reply_text(text='Администратор успешно удален')
        admin.delete_one({'phone': phone})
        return ConversationHandler.END
    elif admin.find_one({'phone': phone}) is  None:
        await update.message.reply_text(text='Администратор c данным номером не был найден в базе(.'
                                             'Попробуй ещё раз /del_admin')
        return ConversationHandler.END


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


async def del_resident_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text='Для удаления резидента из базы напиши его номер в форматье:'
                                         '7XXXXXXXXXX')
    return PHONE_RS_DEL


async def del_resident_end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text
    if find_phone(phone=phone) is None:
        await update.message.reply_text(text='Резидент c данным номером не был найден в базе(.'
                                             'Попробуй ещё раз /del_resident')
    else:
        await update.message.reply_text(text='Резидент успешно удален')
        delet_on_phone(phone=phone)


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
