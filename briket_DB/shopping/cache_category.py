from briket_DB.config import mongodb
from parcer.parcer_sheet import get_markets, get_market_categories
from telegram.ext import ContextTypes

cachedb = mongodb.cache_category


def cache_category(context: ContextTypes.DEFAULT_TYPE):
    for resident in get_markets():
        cachedb.find_one_and_update(filter={'resident': resident},
                                    update={'$unset': {'category': ''}})
        cachedb.find_one_and_update(filter={'resident': resident},
                                    update={'$set': {'category': get_market_categories(resident)}})
    return


def read_category(resident: str):
    category = cachedb.find_one({'resident': resident})['category']
    return category
