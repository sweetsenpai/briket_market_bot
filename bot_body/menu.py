import logging
from uuid import uuid4
from telegram import InlineQueryResultArticle, InputTextMessageContent, Update, InlineQueryResultPhoto
from telegram.ext import ContextTypes
from briket_DB.residents import read_all
from parcer.parcer_sheet import get_market_categories, get_markets

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the inline query. This is run when you type: @botusername <query>"""
    query = update.inline_query.query
    results = []
    for market in read_all():
        results.append(
            InlineQueryResultArticle(
                id=str(uuid4()),
                title=market['resident_name'],
                description=market['description'],
                input_message_content=InputTextMessageContent(market['phone']),
                thumb_url=market['img_url'],
                thumb_width=50,
                thumb_height=50,
            ))
    await update.inline_query.answer(results)



