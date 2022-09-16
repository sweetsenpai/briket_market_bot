from briket_DB.config import mongodb

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
                }},
            'total': price
        })
        return
    else:
        try:
            if user_cart['order_items'][resident][dish] is not None:
                sh_cart.find_one_and_update(filter=user_cart,
                                            update={'$inc': {"order_items.{}.{}.quantity".format(resident, dish): 1}})
                sh_cart.find_one_and_update(filter={"user_id": user_id}, update={'$set': {"total": total(user_id)}})
                return
        except KeyError or TypeError:
            sh_cart.find_one_and_update(filter=user_cart,
                                        update={'$set': {"order_items.{}.{}".format(resident, dish): {
                                            'price': price, 'quantity': 1}}})
            sh_cart.find_one_and_update(filter={"user_id": user_id}, update={'$set': {"total": total(user_id)}})
            return


def remove_dish(user_id: int, resident: str, dish: str) -> None:
    user_cart = sh_cart.find_one({"user_id": user_id})

    try:
        if user_cart['order_items'][resident][dish]['quantity'] > 1:
            sh_cart.find_one_and_update(filter=user_cart,
                                        update={'$inc': {"order_items.{}.{}.quantity".format(resident, dish): -1}})
            sh_cart.find_one_and_update(filter={"user_id": user_id}, update={'$set': {"total": total(user_id)}})
            return

        elif user_cart['order_items'][resident][dish]['quantity'] == 1:
            sh_cart.find_one_and_update(filter=user_cart, update={'$unset': {"order_items.{}.{}".format(resident, dish): ''}})
            sh_cart.find_one_and_update(filter={"user_id": user_id}, update={'$set': {"total": total(user_id)}})
            return
    except KeyError or TypeError: return


def show_cart(user_id: int):
    user_cart = sh_cart.find_one({"user_id": user_id})
    order = user_cart['order_items']

    if order is None: return 'Вы ещё ничего не добавили в вашу корзину'
    cart = ''
    for resident in order.keys():
        for dish in order[resident].keys():
            cart += '{}: {} * {}\n'.format(dish, order[resident][dish]['quantity'], order[resident][dish]['price'])
    cart += 'Итого: {}р.'.format(user_cart['total'])
    return cart


def total(user_id: int):
    user_cart = sh_cart.find_one({"user_id": user_id})['order_items']
    total_sum = 0
    for resident in user_cart.keys():
        for dish in user_cart[resident].keys():
            total_sum += user_cart[resident][dish]['quantity'] * float(user_cart[resident][dish]['price'])

    return total_sum


def get_dish_quantity(user_id: int, resident, dish: str) -> str:
    user_cart = sh_cart.find_one({"user_id": user_id})
    try:
        return ''.join(['[', str(user_cart['order_items'][resident][dish]['quantity']), ']'])
    except KeyError:
        return '[0]'
    except TypeError:
        return '[0]'

