from admin_commands import admin
from briket_DB.sql_main_files.residents import read_one_chatid


def admin_check(chat_id: int) -> bool:
    if admin.find_one(filter={'chat_id': chat_id}) is not None:
        return True
    else:
        return False


def res_check(chat_id: int) -> bool:
    if read_one_chatid(chat_id) is not None:
        return True
    else:
        return False
