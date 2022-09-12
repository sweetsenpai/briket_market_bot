from config import mongodb
from datetime import datetime
from pymongo.collection import ObjectId
from pymongo import ReturnDocument

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


