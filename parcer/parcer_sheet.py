
from briket_DB.passwords import credentials
import gspread
import pandas as pd
import requests
import shutil

sa = gspread.service_account_from_dict(credentials)

sheet = sa.open('Меню')


work_sheets = sheet.worksheets()
work_sheet = sheet.worksheet('KFC')


def get_markets(sheets=work_sheets):
    market_list = []
    for sheet in sheets:
        market_list.append(sheet.title)

    return market_list


def get_market_categories(sheet=work_sheet):
    dataframe = pd.DataFrame(sheet.get_all_records())
    return dataframe['Категория'].unique().tolist()


def get_dish(sheet=work_sheet, cat='Бургеры'):
    df = pd.DataFrame(sheet.get_all_records())
    dt = df.loc[df['Категория'] == cat].loc[df['стоп-лист'] == 'FALSE']
    del dt['Категория']
    del df['стоп-лист']

    return dt.to_dict(orient='split')['data'], sheet


def load_img(img_url):
    file_name = 'menu_img.jpg'
    res = requests.get(img_url, stream=True)
    if res.status_code == 200:
        with open(file_name, 'wb') as f:
            shutil.copyfileobj(res.raw, f)
        return res.content
    else:
        print('Image Couldn\'t be retrieved')





print(get_dish())



