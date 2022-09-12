from briket_DB.config import mongodb
from datetime import datetime
orders_db = mongodb.orders
sh_cart = mongodb.sh_cart


def push_order(user_id: int):
    cart = sh_cart.find_one({"user_id": user_id})
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cart['time'] = time
    cart['status'] = 'new'
    cart['order_num'] = datetime.now().microsecond
    orders_db.insert_one(cart)
    sh_cart.delete_one({"user_id": user_id})
    return


def send_order_residents(order_num: int):
    orders_db.find_one({"order_num": order_num})
    return


push_order(352354383)

