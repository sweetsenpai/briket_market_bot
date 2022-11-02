from briket_DB.config import mongodb
from pymongo import MongoClient
rev_db = mongodb.reviews


def create_rev_res(res_name: str):
    res_rev = {
        'res_name': res_name,
        'posted': list(),
        'moderation': list()
    }
    rev_db.insert_one(res_rev)
    return


def add_new_rev(res_name, text, user_id, admins_list):
    rev_db.find_one_and_update(filter={'res_name': res_name}, update={'':{}})