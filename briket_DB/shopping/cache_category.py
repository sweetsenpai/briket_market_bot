from briket_DB.config import mongodb
from parcer.parcer_sheet import get_markets, get_market_categories, get_dishs
from telegram.ext import ContextTypes

cachedb = mongodb.test


# context: ContextTypes.DEFAULT_TYPE
def cache_category():
    for resident in get_markets():

        if cachedb.find_one_and_update(filter={'resident': resident}, update={'$unset': {'category': ''}}) is None:
            cachedb.insert_one({'resident': resident,
                                'category': get_market_categories(resident)})
        else:
            try:
                for category in get_market_categories(resident):
                    for dish in get_dishs(resident, category):
                        if dish[0] == '':
                            continue
                        try:
                            dish_data = {'Вес': dish[1], 'Цена': dish[2], 'IMG': dish[3],
                                     'стоп-лист': dish[4], 'Белки': dish[5], 'Жиры': dish[6], 'Углеводы': dish[7], 'Описание': dish[8]}
                        except IndexError:
                            dish_data = {'Вес': dish[1], 'Цена': dish[2], 'IMG': dish[3],
                                         'стоп-лист': dish[4], 'Белки': '', 'Жиры': '', 'Углеводы': '',
                                         'Описание': ''}
                        print(dish_data)
                        cachedb.find_one_and_update(filter={'resident': resident},
                                                    update={'$set': {f'category.{category}.{dish[0]}': dish_data}})
            except TypeError:
                continue

    return


def read_category(resident: str):
    try:
        rez = cachedb.find_one({'resident': resident})
        return rez['category']
    except TypeError:
        return

print(cache_category())
