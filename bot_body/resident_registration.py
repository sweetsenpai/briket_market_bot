from telegram import (ReplyKeyboardRemove,
                      Update,
                      ReplyKeyboardMarkup,
                      KeyboardButton)

from telegram.ext import (
    ContextTypes,
    ConversationHandler)
from briket_DB.residents import find_phone, insert_img,insert_email,insert_name,insert_location,insert_description
import logging
import cloudinary
from cloudinary import uploader
cloudinary.config(
  cloud_name="dwexszkh4",
  api_key="677565459774618",
  api_secret="CaPikHBUwKY8zX8aHuHRyeDhxrM"
)

PHONE, NAME, IMG, EMAIL, DESCRIPTION, ADDRES = range(6)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    share_button = KeyboardButton(text='Поделиться номером телефона', request_contact=True)
    key_board = ReplyKeyboardMarkup(one_time_keyboard=True,
                                    keyboard=[[share_button]],
                                    resize_keyboard=True)
    await update.message.reply_text(text='Для начала регистрации необходимо прислать ваш номер телефона',
                                    reply_markup=key_board)
    return PHONE


async def phon_res(update: Update, context: ContextTypes.DEFAULT_TYPE):
    resident = update.message.from_user
    resident_contact = update.message.contact.phone_number
    phone = find_phone(resident_id=update.message.from_user.id, phone=resident_contact)
    if phone is None:
        await update.message.reply_text(
            text='Ваш номер телефона не найден в нашей базе, пожалуйста попросите администратора добавить ваш номер.'
        )
        return
    elif phone is not None:
        logger.info(
            "Contact of {}: {}".format(resident.first_name, resident_contact)
        )
        share_button = KeyboardButton(text='Добавить адрес', request_location=True)
        key_board = ReplyKeyboardMarkup(one_time_keyboard=True,
                                        keyboard=[[share_button]],
                                        resize_keyboard=True)
        await update.message.reply_text('Отлично, ваш номер телефона уже добавлен администратором.',
                                        reply_markup=key_board)
        return ADDRES


async def resident_addres(update: Update, context: ContextTypes.DEFAULT_TYPE):
    resident = update.message.from_user
    resident_location = update.message.location
    logger.info(
        "Location of %s: %f / %f", resident.first_name, resident_location.latitude, resident_location.longitude
    )
    insert_location(resident_id=update.message.from_user.id,
                    location=''.join(str(resident_location)))
    await update.message.reply_text(
        "А теперь добавим название вашего заведения", reply_markup=ReplyKeyboardRemove()
    )
    return NAME


async def resident_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    resident = update.message.from_user
    logger.info("Название заведения: %s: %s", resident.first_name, update.message.text)
    insert_name(resident_id=update.message.from_user.id, name=update.message.text)
    await update.message.reply_text('Отправьте ваш email')
    return EMAIL


async def resident_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    resident = update.message.from_user
    insert_email(resident_id=update.message.from_user.id, email=update.message.text)
    logger.info("email заведения: %s: %s", resident.first_name, update.message.text)
    await update.message.reply_text(text='Отправьте описание вашего заведение которое будут видеть гости')
    return DESCRIPTION


async def resident_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    resident = update.message.from_user
    insert_description(resident_id=update.message.from_user.id, description=update.message.text)
    logger.info("Описание заведения: %s: %s", resident.first_name, update.message.text)
    await update.message.reply_text(
        text='Остался последний шаг, отправте картинку которая будет отображаться в боте,'
             'лучше всего если изображение будет квадратным')
    return IMG


async def resident_img(update: Update, context: ContextTypes.DEFAULT_TYPE):
    resident = update.message.from_user
    file = update.message.photo[-1].file_id
    obj = await context.bot.get_file(file)
    url = cloudinary.uploader.upload(await obj.download())['url']
    insert_img(resident_id=update.message.from_user.id, img=url)
    logger.info('Изображение заведения {} :{}'.format(resident.first_name, url))
    await update.message.reply_text('Поздравляем, регистрация завершена.\n'
                                    'Чтобы ознакомиться с инструкцией нажми сюда -> /instraction')
    return ConversationHandler.END


async def resident_end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    resident = update.message.from_user
    logger.info("User %s canceled the conversation.", resident.first_name)
    await update.message.reply_text(
        text='Регистрация прервана!'
    )
    return ConversationHandler.END
