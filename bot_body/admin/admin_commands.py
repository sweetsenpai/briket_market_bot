from telegram import (Update,
                      ReplyKeyboardMarkup,
                      KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup)

from telegram.ext import (
    ContextTypes,
    ConversationHandler)
from briket_DB.config import mongodb
import logging
from briket_DB.sql_main_files.residents import create, read_all, read_one_chatid
from briket_DB.reports.report_main import get_resident_report_day, get_resident_report_month
from text_integration.pastebin_integration import get_text_api
from bot_body.admin.access_level import admin_check, res_check
admin_db = mongodb.admin
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

PHONE_AD_ADD, PHONE_RS_ADD = range(2)


async def add_new_admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if admin_check(update.message.from_user.id) is False:
        await update.message.reply_text(text='Вам отказанно в праве доступа.')
        return ConversationHandler.END
    await update.message.reply_text(text=get_text_api('0Gsm3Vnt'))
    return PHONE_AD_ADD


async def add_new_admin_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text
    admin_db.insert_one({'phone': phone})
    await update.message.reply_text(text='Номер нового администратора({}) успешно добавлен, '
                                         'теперь новый админ может пройти регистрацию.'
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
    if admin_check(update.message.from_user.id) is False:
        await update.message.reply_text(text='Вам отказанно в праве доступа.')
        return
    if mongodb.admin_db.find_one({'chat_id': admin_id}) is None:
        await update.message.reply_text(text=get_text_api('trhpLPsm'))
        return
    else:
        await update.message.reply_text(
            text='Выберете резидента которого необходимо удалить:',
            reply_markup=del_resident_keyboard()
        )
        return


def del_admin_keyboard(admin_id: int):
    button_admin = []
    for admins in mongodb.admin_db.find():
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
    if admin_check(update.message.from_user.id) is False:
        await update.message.reply_text(text='Вам отказанно в праве доступа.')
        return

    if mongodb.admin_db.find_one({'chat_id': admin_id}) is None:
        await update.message.reply_text(text=get_text_api('trhpLPsm'))
        return
    else:
        await update.message.reply_text(
            text='Выберете номер администратора которого необходимо удалить из базы:',
            reply_markup=del_admin_keyboard(admin_id=admin_id)
        )
        return


async def add_new_resident_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if admin_check(update.message.from_user.id) is False:
        await update.message.reply_text(text='Вам отказанно в праве доступа.')
        return ConversationHandler.END
    await update.message.reply_text(text=get_text_api('Cxht7gaQ'))
    return PHONE_RS_ADD


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
                                         'Для прохождения регистрации необходимо написать в чат:\n /registration'.format(
        phone))
    return ConversationHandler.END


async def cancel_conv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text='Действие прервано!')
    return ConversationHandler.END


async def admin_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if admin_check(update.message.from_user.id) is False:
        await update.message.reply_text(text='Вам отказанно в праве доступа.')
        return
    await update.message.reply_text(text=get_text_api('Fy9ejgAv'))
    return


async def resident_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if admin_check(update.message.from_user.id) is False or res_check(update.message.from_user.id) is False:
        await update.message.reply_text(text='Вам отказанно в праве доступа.')
        return
    await update.message.reply_text(text=get_text_api('ph3Z6zLK'))
    return


async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    id = update.message.from_user.id
    if mongodb.admin_db.find_one({'chat_id': id}) is not None:
        day = KeyboardButton(text='За день')
        mounth = KeyboardButton(text='Месячный')
        keyboard = ReplyKeyboardMarkup(keyboard=[[day], [mounth]])
        await update.message.reply_text(text='Выберете вид отчета на клавиатуре:', reply_markup=keyboard)
        return
    if res_check(id) is not None:
        day = KeyboardButton(text='За день')
        mounth = KeyboardButton(text='Месячный')
        keyboard = ReplyKeyboardMarkup(keyboard=[[day], [mounth]])
        await update.message.reply_text(text='Выберете вид отчета на клавиатуре:', reply_markup=keyboard)
        return


async def day_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.from_user.id
    if admin_db.find_one(filter={'chat_id':chat_id}) is not None:
        for residen in read_all():
            await update.message.reply_text(text=get_resident_report_day(residen['resident_name']), parse_mode='HTML')
            return
    if read_one_chatid(chat_id) is not None:
        await update.message.reply_text(text=get_resident_report_day(read_one_chatid(chat_id)['resident_name']), parse_mode='HTML')
        return
    await update.message.reply_text(text="У вас нет доступа к этой функции(",
                                    parse_mode='HTML')
    return


async def mouth_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.from_user.id
    if admin_db.find_one(filter={'chat_id': chat_id}) is not None:
        for residen in read_all():
            await update.message.reply_text(text=get_resident_report_month(residen['resident_name']), parse_mode='HTML')
            return
    if read_one_chatid(chat_id) is not None:
        await update.message.reply_text(text=get_resident_report_month(read_one_chatid(chat_id)['resident_name']), parse_mode='HTML')
        return
    await update.message.reply_text(text="У вас нет доступа к этой функции(",
                                    parse_mode='HTML')
    return


async def mouth_report_job(context: ContextTypes.DEFAULT_TYPE):
    admin_report_data = ""
    for residen in read_all():
        report_data = get_resident_report_month(residen['resident_name'])
        admin_report_data += report_data + '\n'
        await context.bot.sendMessage(chat_id=residen['chat_id'],
                                      text=report_data, parse_mode='HTML')
    for admins in admin_db.find({'chat_id': {'$exists': True}}):
        await context.bot.sendMessage(chat_id=admins['chat_id'],
                                      text=admin_report_data, parse_mode='HTML')
    return


async def day_report_job(context: ContextTypes.DEFAULT_TYPE):
    admin_report_data = ""
    for residen in read_all():

        report_data = get_resident_report_day(residen['resident_name'])
        admin_report_data += report_data + '\n'
        await context.bot.sendMessage(chat_id=residen['chat_id'],
                                      text=report_data, parse_mode='HTML')
    for admins in admin_db.find({'chat_id': {'$exists': True}}):
        await context.bot.sendMessage(chat_id=admins['chat_id'],
                                      text=admin_report_data, parse_mode='HTML')
    return
