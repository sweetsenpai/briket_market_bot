import telegram.error

from briket_DB.sql_main_files.customers import read_all
import pandas as pd
import gspread as gsp
from telegram.ext import ContextTypes
from parcer.parcer_sheet import sa
import json
# briketbot2022@gmail.com
#BriketBot2022


async def user_data_updater(context: ContextTypes.DEFAULT_TYPE):
    user_list = []
    for user in read_all():
        try:
            msg_data = await context.bot.send_message(chat_id=user['chat_id'],
                                     text='.', disable_notification=True)
            user['status'] = 'Активен'
            user['nickname'] = msg_data['chat']['username']
            await context.bot.delete_message(chat_id=user['chat_id'], message_id=msg_data['message_id'])
        except telegram.error.BadRequest:
            user['status'] = 'Не активен'
            user['nickname'] = 'username'
        user_list.append(user)
    df = pd.DataFrame(user_list)
    del df['customer_id']
    del df['chat_id']
    del df['addres']
    new_df = ((df.reindex(columns=['name', 'phone', 'email', 'addres', 'status'])).fillna('-')).rename(
        columns={'name': "Имя", 'phone': "Телефон", "addres": "Адрес", "status": "Статус"})

    user_sheet = sa.open('Данные пользователей')
    user_work = user_sheet.worksheet('Пользователи')
    user_work.update([new_df.columns.values.tolist()] + new_df.values.tolist())
    return


