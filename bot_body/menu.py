import logging
from html import escape
from uuid import uuid4
from telegram import InlineQueryResultArticle, InputTextMessageContent, Update, InlineQueryResultPhoto
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

#https://docs.python-telegram-bot.org/en/stable/telegram.inlinequeryresultphoto.html#telegram.InlineQueryResultPhoto
#https://github.com/python-telegram-bot/python-telegram-bot/wiki/Code-snippets#build-a-menu-with-buttons
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the inline query. This is run when you type: @botusername <query>"""
    query = update.inline_query.query

    if query == "":
        return

    results = [
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="Caps",
            input_message_content=InputTextMessageContent(query.upper()),
        ),
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="Bold",
            input_message_content=InputTextMessageContent(
                f"<b>{escape(query)}</b>", parse_mode=ParseMode.HTML
            ),
        ),
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="Italic",
            input_message_content=InputTextMessageContent(
                f"<i>{escape(query)}</i>", parse_mode=ParseMode.HTML
            ),
        ),
        InlineQueryResultPhoto(
            id=str(uuid4()),
            title='TEST',
            photo_url='https://www.codeproject.com/KB/GDI-plus/ImageProcessing2/img.jpg',
            photo_width=50,
            photo_height=50,
            thumb_url='https://www.codeproject.com/KB/GDI-plus/ImageProcessing2/img.jpg'
        )
    ]

    await update.inline_query.answer(results)


