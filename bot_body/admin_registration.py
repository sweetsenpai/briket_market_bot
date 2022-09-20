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

async def reg_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):

