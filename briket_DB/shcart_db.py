from briket_DB.config import mongodb
import json
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
        return
    else:
        try:
            if user_cart['order_items'][resident][dish] is not None:
                sh_cart.find_one_and_update(filter=user_cart,
                                            update={'$inc': {"order_items.{}.{}.quantity".format(resident, dish): 1}})
                return
        except KeyError:
            sh_cart.find_one_and_update(filter=user_cart,
                                        update={'$set': {"order_items.{}.{}".format(resident, dish): {
                                            'price': price, 'quantity': 1}}})
            return


def remove_dish(user_id: int, resident: str, dish: str) -> None:
    user_cart = sh_cart.find_one({"user_id": user_id})
    if user_cart['order_items'][resident][dish]['quantity'] > 1:
        sh_cart.find_one_and_update(filter=user_cart,
                                    update={'$inc': {"order_items.{}.{}.quantity".format(resident, dish): -1}})
        return
    elif user_cart['order_items'][resident][dish]['quantity'] == 1:
        print('-------------------------------')
        sh_cart.find_one_and_update(filter=user_cart, update={'$unset': {"order_items.{}.{}".format(resident, dish): ''}})
        return


def show_cart(user_id: int):
    user_cart = sh_cart.find_one({"user_id": user_id})
    if user_cart is None: return 'Вы ещё ничего не добавили в вашу корзину'
    x = json.dumps(user_cart['order_items'])
    y = json.loads(x)

    return


show_cart(352354383)