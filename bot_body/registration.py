import logging
from briket_DB.customers import find_id, create, update_addres
from telegram import ReplyKeyboardRemove, Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ContextTypes,
    ConversationHandler,

)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

PHONE, LOCATION, INFO = range(3)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    share_button = KeyboardButton(text='Share my contact', request_contact=True)

    key_board = ReplyKeyboardMarkup(one_time_keyboard=True,
                                    keyboard=[[share_button]],
                                    resize_keyboard=False)

    if find_id(chat_id) is not None:
        await update.message.reply_text('Рад видеть тебя снова! Нажми /menu')

    elif find_id(chat_id) is None:
        await update.message.reply_text('Давай знакомиться!, '
                                        'пришли мне свой номер телефона',
                                        reply_markup=key_board)

        return PHONE


async def phone(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.message.from_user
    user_contact = update.message.contact.phone_number

    logger.info(
        "Contact of {}: {}".format(user.first_name, user_contact)
    )

    share_button = KeyboardButton(text='Share my location', request_location=True)
    key_board = ReplyKeyboardMarkup(one_time_keyboard=True,
                                    keyboard=[[share_button]],
                                    resize_keyboard=False)

    await update.message.reply_text('Сяп, теперь пришли мне свой адрес или нажми /skip',
                                    reply_markup=key_board)
    customer = {'chat_id': user.id,
                'phone': str(user_contact),
                'addres': str(''),
                'disc_status': True}
    create(customer)
    return LOCATION


async def location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_location = update.message.location
    logger.info(
        "Location of %s: %f / %f", user.first_name, user_location.latitude, user_location.longitude
    )
    await update.message.reply_text(
        "А теперь расскажи о себе", reply_markup=ReplyKeyboardRemove()
    )
    update_addres(user.id, str([user_location.latitude, user_location.longitude]))
    return INFO


async def skip_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Skips the location and asks for info about the user."""
    user = update.message.from_user
    logger.info("User %s did not send a location.", user.first_name)
    await update.message.reply_text(
        "Как хочешь("
    )

    return INFO


async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    logger.info("info of %s: %s", user.first_name, update.message.text)
    await update.message.reply_text("Спасибо")
    await update.message.reply_text(
        "Рад был познакомиться! Нажми /menu", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)

    return ConversationHandler.END
