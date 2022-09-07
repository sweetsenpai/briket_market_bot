
from briket_DB.passwords import credentials
import gspread
import pandas as pd
import requests
import shutil

sa = gspread.service_account_from_dict(credentials)

sheet_main = sa.open('Меню')


work_sheets = sheet_main.worksheets()
work_sheet = sheet_main.worksheet('KFC')


def get_markets(sheets=work_sheets):
    market_list = []
    for sheet in sheets:
        market_list.append(sheet.title)

    return market_list


def get_market_categories(work_sheet:str):
    ws = sheet_main.worksheet(work_sheet)
    dataframe = pd.DataFrame(ws.get_all_records())
    return dataframe['Категория'].unique().tolist()


def get_dishs(sheet='KFC', cat='Бургеры'):
    ws = sheet_main.worksheet(sheet)
    df = pd.DataFrame(ws.get_all_records())
    dt = df.loc[df['Категория'] == cat].loc[df['стоп-лист'] == 'FALSE']
    del dt['Категория']
    del df['стоп-лист']

    return dt.to_dict(orient='split')['data']


def get_one_dish(sheet='KFC', name='Шефбургер'):
    ws = sheet_main.worksheet(sheet)
    df = pd.DataFrame(ws.get_all_records())

    dt = df.loc[df['Название'] == name]

    del dt['Категория'], df['стоп-лист']

    return dt.to_dict(orient='split')['data']


def load_img(img_url):
    file_name = 'menu_img.jpg'
    res = requests.get(img_url, stream=True)
    if res.status_code == 200:
        with open(file_name, 'wb') as f:
            shutil.copyfileobj(res.raw, f)
        return res.content
    else:
        print('Image Couldn\'t be retrieved')








