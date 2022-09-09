from briket_DB.config import mongodb
from parcer.parcer_sheet import get_one_dish
from pymongo.collection import ObjectId
from pymongo import ReturnDocument
"""
_id: int
user_id: int
order_items: dict[resident: name, category:name, dish:name, quantity: int, price: int]
sum: int
"""
sh_cart = mongodb.sh_cart


def add_dish(user_id: int, resident: str, dish: str, price: str) -> None:
    user_cart = sh_cart.find_one({"user_id": user_id})
    if user_cart is None:
        sh_cart.insert_one({
            'user_id': user_id,
            'order_items': {
                resident: {
                    dish: {
                        'price': price,
                        'quantity': 1}
                }}
        })
    elif dish in user_cart['order_items'][resident]:
        sh_cart.find_one_and_update(filter=user_cart,
                                    update={'$inc': {"order_items.{}.{}.quantity".format(resident, dish): 1}})
    elif user_cart['order_items'][resident] is not None:
        sh_cart.find_one_and_update(filter=user_cart,
                                    update={'$set': {"order_items.{}.{}".format(resident, dish): {
                                        'price': price, 'quantity': 1}}})

    return


def remove_dish(user_id: int, resident: str, dish: str) -> None:
    user_cart = sh_cart.find_one({"user_id": user_id})
    if user_cart['order_items'][resident][dish]['quantity'] > 1:
        sh_cart.find_one_and_update(filter=user_cart,
                                    update={'$inc': {"order_items.{}.{}.quantity".format(resident, dish): -1}})
    elif user_cart['order_items'][resident][dish]['quantity'] <= 1:
        sh_cart.find_one_and_update(filter=user_cart, update={'$unset': {dish: ''}})
    return
