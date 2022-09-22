from telegram import (ReplyKeyboardRemove,
                      Update,
                      ReplyKeyboardMarkup,
                      KeyboardButton)

from telegram.ext import (
    ContextTypes,
    ConversationHandler)
from briket_DB.config import mongodb
import logging

admin = mongodb.admin

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

PHONE, EMAIL = range(2)


async def reg_admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    share_button = KeyboardButton(text='Поделиться номером телефона', request_contact=True)
    key_board = ReplyKeyboardMarkup(one_time_keyboard=True,
                                    keyboard=[[share_button]],
                                    resize_keyboard=False)
    await update.message.reply_text(text='Необходимо проверить, внес ли кто-нибудь вас в базу администраторов',
                                    reply_markup=key_board)
    return PHONE


async def admin_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.contact.phone_number
    resident = admin.find_one({"phone": phone})
    if resident is None:
        await update.message.reply_text('Ксожалению мы не нашли вашего номера в нашей базе')

    elif resident is not None:
        admin.delete_one({"phone": phone})
        new_admin = {
            'chat_id': update.message.from_user.id,
            'phone': phone,
            'email': ''
        }
        admin.insert_one(new_admin)
        await update.message.reply_text(text='Отлично, вы прошли проверку!\n'
                                             'Теперь пришлите ваш email, '
                                             'в дальнейшем на него будет приходит отчет о продажах через бота.')
        return EMAIL


async def admin_final(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text
    admin.find_one_and_update(
        filter={"chat_id": update.message.from_user.id},
        update={'$set': {'email': email}}
    )
    await update.message.reply_text(text='Регистрация завершена.\n'
                                         'Чтобы ознакомиться с интрукцией нажми сюда -> /admin_info')
    return ConversationHandler.END


async def admin_exit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Регистрация прервана!')
    return ConversationHandler.END
