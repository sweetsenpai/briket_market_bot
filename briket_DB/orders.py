from config import mongodb
from datetime import datetime
from pymongo.collection import ObjectId
from pymongo import ReturnDocument

"""
orders schema:
_id: int
user_id: int
date: char 
order_items: dict[resident: name, category:name, dish:name, quantity: int, price: int]
sum: int
status: new/prepare/delivery/finished/canceled
commentary: str/None
"""
orders = mongodb.orders
test_order = [{'resident': 'KFC', 'category': 'бургеры', 'dish': 'чикенбургер','quantity': 3, 'price': 100},
             {'resident': 'KFC', 'category': 'картошка', 'dish': 'по-деревенски','quantity': 5, 'price': 50},
             {'resident': 'KFC', 'category': 'напитки', 'dish': 'Cool-Cola','quantity':2 , 'price': 70}]

test_order2 = [{'resident': 'Вкус очка', 'category': 'бургеры', 'dish': 'БигМак','quantity': 10, 'price': 500},
             {'resident': 'Вкус очка', 'category': 'картошка', 'dish': 'картофель фри','quantity': 15, 'price': 30},
             {'resident': 'Вкус очка', 'category': 'напитки', 'dish': 'Тархун','quantity':9 , 'price': 75}]

test_order3 = [{'resident': 'Бургер Кинг', 'category': 'бургеры', 'dish': 'Стейкхаус','quantity': 1, 'price': 490},
             {'resident': 'Бургер Кинг', 'category': 'картошка', 'dish': 'картофель фри','quantity': 15, 'price': 73},
             {'resident': 'Бургер Кинг', 'category': 'напитки', 'dish': 'Bud','quantity':9 , 'price': 89}]

status_list = ['new', 'waiting for confirmation', 'prepare','delivery', 'finished']

def cancel_order(order_id: int, reason: str):
    objInstance = ObjectId(order_id)
    order = orders.find_one({"_id": objInstance})
    order_update = orders.update_one(filter={"_id": objInstance},
                                     update={'$set': {"status": 'canceled', 'commentary': reason}})
    return orders.find_one({"_id": objInstance})


def status_step_step_back(order_id):
    objInstance = ObjectId(order_id)
    order = orders.find_one({"_id": objInstance})

    if order['status'] == 'new':
        return 'This is new order!'
    else:
        new_status = status_list[status_list.index(order['status']) - 1]

    order_update = orders.update_one(filter={"_id": objInstance},
                                     update={'$set': {"status": new_status}})
    return orders.find_one({"_id": objInstance})


def status_step_up(order_id):
    objInstance = ObjectId(order_id)
    order = orders.find_one({"_id": objInstance})
    if order['status'] == 'finished':
        return 'This order allready finished!'
    else:
        new_status = status_list[status_list.index(order['status']) + 1]

    order_update = orders.update_one(filter={"_id": objInstance},
                                     update={ '$set': { "status" : new_status}})
    return orders.find_one({"_id": objInstance})

def add_more_or_less(order_id, resident:str, new_quantity:int, dish:str):
    objInstance = ObjectId(order_id)
    order = orders.find_one({"_id": objInstance})
    if orders.find_one({"_id": objInstance}) is not None:
        orders.update_one(filter={"_id": objInstance, 'resident': resident, 'dish': dish},
                          update={'$set': {"quantity": new_quantity}})
    return orders.find_one({"_id": objInstance})



def get_sum(dishes: dict):
    sum_price = 0
    for dish in dishes:
        sum_price+=dish['quantity'] * dish['price']
    return sum_price


def new_order(order_obj: list, user_id: int, comment=''):
    order = orders.insert_one({'date':datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                       'user_id': user_id,
                       'order_items':order_obj,
                       'total': get_sum(order_obj),
                       'status':'new',
                       'commentary': comment})
    return order


#print(cancel_order('62f11cafac0d21f872fef48e', 'Run out of burgers'))


