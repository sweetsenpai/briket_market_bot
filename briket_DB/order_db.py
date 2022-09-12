from briket_DB.config import mongodb
from datetime import datetime
orders_db = mongodb.orders
sh_cart = mongodb.sh_cart


def push_order(user_id: int):
    cart = sh_cart.find_one({"user_id": user_id})
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cart['time'] = time
    orders_db.insert_one(cart)
    return

