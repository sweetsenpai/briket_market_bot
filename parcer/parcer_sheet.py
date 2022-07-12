"""
1.Получить список ресторнов - есть
2.Получить категории меню/блюд - есть
3.Получить блюда категории
"""

import gspread
import numpy as np
import pandas as pd

sa = gspread.service_account(filename='service_account.json')

sheet = sa.open('Меню')


work_sheets = sheet.worksheets()
work_sheet = sheet.worksheet('KFC')


def get_markets(sheets=work_sheets):
    market_list = []
    for sheet in sheets:
        market_list.append(sheet.title)

    return market_list


def get_market_categories(sheet=work_sheet):
    dataframe = pd.DataFrame(work_sheet.get_all_records())
    return dataframe['Категория'].unique().tolist()


def get_dish(sheet=work_sheet, cat='Бургеры'):
    df = pd.DataFrame(work_sheet.get_all_records())
    dt = df.loc[df['Категория'] == cat]
    del dt['Категория']

    return dt.to_dict(orient='split')['data'][1]









