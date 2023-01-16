import pandas as pd
from briket_DB.config import mongodb
from telegram.ext import ContextTypes

cachedb = mongodb.test


# context: ContextTypes.DEFAULT_TYPE

def cache_menu(context: ContextTypes.DEFAULT_TYPE):
    full_data = sa.open('Меню').worksheets()
    for res in full_data:
        res_df = pd.DataFrame(res.get_all_records())
        if cachedb.find_one_and_update(filter={'resident': res.title}, update={'$unset': {'category': ''}}) is None:
            cachedb.insert_one({'resident': res.title,
                                'category': get_market_categories(res_df)})
        else:
            try:
                res.get_all_records()
                for category in get_market_categories(res_df):
                    for dish in get_dishs(res_df, category):
                        if dish[0] == '':
                            continue
                        dish_data = {'Вес': dish[1], 'Цена': dish[2], 'IMG': dish[3],
                                         'Белки': dish[4], 'Жиры': dish[5], 'Углеводы': dish[6], 'Описание': dish[7]}

                        print(dish_data)
                        cachedb.find_one_and_update(filter={'resident': res.title},
                                                    update={'$set': {f'category.{category}.{dish[0]}': dish_data}})
            except TypeError:
                continue

    return


def read_category(resident: str):
    try:
        rez = cachedb.find_one({'resident': resident})['category'].keys()
        return rez
    except TypeError:
        return


def get_dishs_db(resident, category):
    return cachedb.find_one(filter={'resident': resident})['category'][category]

