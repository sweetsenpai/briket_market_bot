from briket_DB.passwords import credentials
import gspread
import pandas as pd
import requests
import shutil
import os
sa = gspread.service_account_from_dict(credentials)

# TODO: сделать  кэш всех позиций резидента


def get_markets():
    sheet_main = sa.open('Меню')
    sheets = sheet_main.worksheets()
    market_list = []
    for sheet in sheets:
        market_list.append(sheet.title)

    return market_list


def get_market_categories(ws: str):
    try:

        sheet_main = sa.open('Меню')
        ws = sheet_main.worksheet(ws)
        dataframe = pd.DataFrame(ws.get_all_records())
        for index, row in dataframe.iterrows():
            print(row)
            print('------------------------------')
        cat_list = dataframe['Категория'].unique().tolist()
        cat_list = list(filter(None, cat_list))
        return cat_list
    except KeyError:
        return


def get_dishs(sheet='KFC', cat='Бургеры'):

    sheet_main = sa.open('Меню')
    ws = sheet_main.worksheet(sheet)
    df = pd.DataFrame(ws.get_all_records())
    dt = df.loc[df['Категория'] == cat].loc[df['стоп-лист'] == 'FALSE']
    del dt['Категория']
    del dt['стоп-лист']
    dt.fillna('‎')
    return dt.to_dict(orient='split')['data']


def get_one_dish(sheet='KFC', name='Шефбургер'):
    sheet_main = sa.open('Меню')
    ws = sheet_main.worksheet(sheet)
    df = pd.DataFrame(ws.get_all_records())
    dt = df.loc[df['Название'] == name]
    del dt['Категория'], df['стоп-лист']
    dt.fillna('‎')
    return dt.to_dict(orient='split')['data']


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


sh = sa.open('Меню')
x = sh.worksheets()

for i in x:
    df = pd.DataFrame(i.get_all_records())
    print(i.title)
    for ind, rows in df.iterrows():
        print(rows)
        print('-------------')




