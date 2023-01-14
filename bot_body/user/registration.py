import logging
from briket_DB.shopping.promotions import chek_personal_code
from briket_DB.sql_main_files.customers import find_id, create, insert_new_addres, inser_new_name, insert_new_email
from briket_DB.sql_main_files.residents import find_phone
from telegram import ReplyKeyboardRemove, Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler)
from text_integration.pastebin_integration import get_text_api
from bot_body.user.addresses import show_addresses
from bot_body.functional_key import customer_keyboard
from bot_body.menu import menu
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

PHONE, LOCATION, INFO, EMAIL = range(4)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    share_button = KeyboardButton(text='Share my contact', request_contact=True)

    key_board = ReplyKeyboardMarkup(one_time_keyboard=True,
                                    keyboard=[[share_button]],
                                    resize_keyboard=False)

    if find_id(chat_id) is not None:
        await update.message.reply_text(get_text_api('KBermmJp'))

    elif find_id(chat_id) is None:
        await update.message.reply_text(text=get_text_api('a6EZbbzk'),
                                        reply_markup=key_board)

        return PHONE


async def phone(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.message.from_user

    try:
        user_contact = update.message.contact.phone_number
        user_contact = user_contact.replace('+', '')
    except AttributeError:
        raw_number = update.message.text.replace('+', '')
        raw_number = raw_number.replace(' ', '')
        raw_number = raw_number.replace('-', '')
        raw_number = raw_number.replace('(', '')
        raw_number = raw_number.replace(')', '')
        raw_number = list(raw_number)
        raw_number[0] = '7'
        user_contact = ''.join(raw_number)

    resident_search = find_phone(user.id, user_contact)
    if resident_search is not None:
        await context.bot.send_message(chat_id=resident_search['chat_id'],
                                       text='Администратор внес вас в раздел резидентов.\n'
                                            'Чтобы пройти регистрацию от лица заведения,\n'
                                            'нажмите сюда -> /registration')
        return ConversationHandler.END
    logger.info(
        "Contact of {}: {}".format(user.first_name, user_contact)
    )

    await update.message.reply_text(text=get_text_api('MBMfCNhN'))
    customer = {'chat_id': user.id,
                'phone': str(user_contact),
                'addres': str('')}
    create(customer)
    return LOCATION


async def location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.message.from_user
        user_location = update.message.location
        logger.info(
            "Location of %s: %f / %f", user.first_name, user_location.latitude, user_location.longitude
        )
        await update.message.reply_text(
            text=get_text_api('aANQhGQP'), reply_markup=ReplyKeyboardRemove()
        )
        insert_new_addres(user.id, str([user_location.latitude, user_location.longitude]))
    except:
        user = update.message.from_user
        user_location = update.message.text
        await update.message.reply_text(
            "Как тебя зовут?", reply_markup=ReplyKeyboardRemove()
        )
        insert_new_addres(user.id, user_location)

    return INFO


async def skip_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info("User %s did not send a location.", user.first_name)
    await update.message.reply_text(
        "Как хочешь("
    )

    return INFO


async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.message.text
    inser_new_name(chat_id=update.message.from_user.id,
                   name=user_name)
    await update.message.reply_text("Спасибо")
    await update.message.reply_text(
        text=get_text_api('jTrJc5RZ'), reply_markup=ReplyKeyboardRemove()
    )
    return EMAIL


async def email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_mail = update.message.text
    insert_new_email(chat_id=update.message.from_user.id,
                     email=user_mail)
    await update.message.reply_text("Регистрация успешно закончена!")
    await menu(update, context)
    await customer_keyboard(update, context)
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)

    return ConversationHandler.END


async def custommer_faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text=get_text_api('8cyyM90u'))
    return


async def custommer_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    user = find_id(user_id)
    if user is None:
        await update.message.reply_text(text='Пожалуйста, пройдите регистрацию \n'
                                             'чтобы получить персональный промокод на скидку.')
        return
    acc_info = 'Привет, {}!\n' \
               'Телефон: {}\n' \
           'Персональный промокд на скиду: <b>{}</b>\n'.format(user['name'], user['phone'],chek_personal_code(user_id))
    await update.message.reply_text(text=acc_info, parse_mode='HTML', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
        text='Мои заказы',
        callback_data='PO,0'
    )]]))
    await show_addresses(update, context)
    return
