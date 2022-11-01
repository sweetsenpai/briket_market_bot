
from briket_DB.passwords import credentials
import gspread
import pandas as pd
import requests
import shutil
import os

sa = gspread.service_account_from_dict(credentials)

#sheet_main = sa.open('Меню')


#work_sheets = sheet_main.worksheets()
#work_sheet = sheet_main.worksheet('KFC')


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
        return dataframe['Категория'].unique().tolist()
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
    sheet_main.add_worksheet(title=resident_name, rows="100", cols="10")
    return






