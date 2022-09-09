import logging
from briket_DB.shcart_db import add_dish, remove_dish
from telegram import (InlineQueryResultArticle,
                      InputTextMessageContent,
                      Update,
                      InlineKeyboardMarkup,
                      InlineKeyboardButton,
                      InlineQueryResultPhoto)
from telegram.ext import ContextTypes
from bot_body.main import main

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def call_back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    cb_data = query.data.split(',')
    logger.info(
        "Callback data: {}".format(cb_data)
    )
    if cb_data[0] == 'add':
        add_dish(user_id=query.from_user.id, resident=cb_data[1], dish=cb_data[2], price=cb_data[3])
        await query.answer()
    elif cb_data[0] == 'minus':
        remove_dish(user_id=query.from_user.id, resident=cb_data[1], dish=cb_data[2])
        await query.answer()
    elif cb_data[0] == 'cart':

        update.MESSAGE.
        await query.answer()


