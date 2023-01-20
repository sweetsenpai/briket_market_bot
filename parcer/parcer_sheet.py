from briket_DB.passwords import credentials
import gspread
import pandas as pd
import requests
import shutil
from briket_DB.config import mongodb
from telegram.ext import ContextTypes
import os

sa = gspread.service_account_from_dict(credentials)
cachedb = mongodb.cache_category


def get_markets():
    sheet_main = sa.open('Меню')
    sheets = sheet_main.worksheets()
    market_list = []
    for sheet in sheets:
        market_list.append(sheet.title)

    return market_list


def get_market_categories(dataframe: pd.DataFrame):
    try:
        cat_list = dataframe['Категория'].unique().tolist()
        cat_list = list(filter(None, cat_list))
        return cat_list
    except KeyError:
        return


def get_dishs(df: pd.DataFrame, cat: str):
    dt = df.loc[df['Категория'] == cat].loc[df['стоп-лист'] == 'FALSE']
    del dt['Категория']
    del dt['стоп-лист']
    dt.fillna('‎')
    return dt.to_dict(orient='split')['data']


def get_one_dish(resident, name='Шефбургер'):
    for category in read_category(resident):
        try:
            return get_dishs_db(resident, category)[name]
        except KeyError:
            continue


def load_img(img_url):
    file_name = 'menu_img.jpg'
    res = requests.get(img_url, stream=True)
    if res.status_code == 200:
        with open(file_name, 'wb') as f:
            shutil.copyfileobj(res.raw, f)
            os.remove(file_name)
        return res.content
    else:
        print('Image Couldn\'t be retrieved')


def create_new_table(resident_name: str):
    sheet_main = sa.open('Меню')
    try:
        sheet_main.add_worksheet(title=resident_name, rows="100", cols="10")
    except gspread.exceptions.APIError:
        pass
    return


def find_dish(sheet='KFC', dish='Шефбургер'):
    sheet_main = sa.open('Меню')
    ws = sheet_main.worksheet(sheet)
    df = pd.DataFrame(ws.get_all_records())
    check_dish = df.loc[df['стоп-лист'] == 'FALSE']
    del check_dish['стоп-лист']
    check_dish.fillna('‎')
    return check_dish.loc[check_dish['Название'] == dish].to_dict(orient='split')['data']


async def cache_menu(context: ContextTypes.DEFAULT_TYPE):
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

                        cachedb.find_one_and_update(filter={'resident': res.title},
                                                    update={'$set': {f'category.{category}.{dish[0]}': dish_data}})
            except TypeError:
                continue

    return


def read_category(resident: str):
    try:
        rez = cachedb.find_one({'resident': resident})['category'].keys()
        return rez
    except TypeError or KeyError:
        return


def get_dishs_db(resident, category):
    result_dish = cachedb.find_one({'resident': resident})
    return result_dish['category'][category]




