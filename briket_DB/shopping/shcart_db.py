from briket_DB.config import mongodb
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from parcer.parcer_sheet import get_one_dish
sh_cart = mongodb.sh_cart


def add_dish(user_id: int, resident: str, dish: str, price: str, amount=0) -> None:
    user_cart = sh_cart.find_one({"user_id": user_id})
    if user_cart is None:
        if amount != 0:
            sh_cart.insert_one({
                'user_id': user_id,
                'order_items': {
                    resident: {
                        dish: {
                            'price': round(float(price), 2),
                            'quantity': amount}
                    }},
                'total': amount*round(float(price), 2)
            })
            return
        else:
            sh_cart.insert_one({
                'user_id': user_id,
                'order_items': {
                    resident: {
                        dish: {
                            'price': round(float(price), 2),
                            'quantity': 1}
                    }},
                'total': price
            })
            return
    else:
        try:
            if user_cart['order_items'][resident][dish] is not None:
                if amount != 0:
                    sh_cart.find_one_and_update(filter=user_cart,
                                                update={
                                                    '$inc': {"order_items.{}.{}.quantity".format(resident, dish): amount}})
                    return
                else:
                    sh_cart.find_one_and_update(filter=user_cart,
                                                update={'$inc': {"order_items.{}.{}.quantity".format(resident, dish): 1}})
                sh_cart.find_one_and_update(filter={"user_id": user_id}, update={'$set': {"total": total(user_id)}})
                return
        except KeyError or TypeError:
            sh_cart.find_one_and_update(filter=user_cart,
                                        update={'$set': {"order_items.{}.{}".format(resident, dish): {
                                            'price': round(float(price), 2), 'quantity': 1}}})
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
    try:
        order = user_cart['order_items']
        cart = ''
        for resident in order.keys():
            for dish in order[resident].keys():
                cart += '{}: {} * {}\n'.format(dish, order[resident][dish]['quantity'], order[resident][dish]['price'])
        cart += 'Итого: {}р.'.format(user_cart['total'])
        return cart
    except TypeError:
        return 'Тут ничего нет'


def total(user_id: int):
    user_cart = sh_cart.find_one({"user_id": user_id})['order_items']
    total_sum = 0
    for resident in user_cart.keys():
        for dish in user_cart[resident].keys():
            total_sum += user_cart[resident][dish]['quantity'] * float(user_cart[resident][dish]['price'])

    return round(total_sum, 2)


def get_dish_quantity(user_id: int, resident, dish: str) -> str:
    user_cart = sh_cart.find_one({"user_id": user_id})
    try:
        return ''.join(['[', str(user_cart['order_items'][resident][dish]['quantity']), ']'])
    except KeyError:
        return '[0]'
    except TypeError:
        return '[0]'


async def empty_shcart(user_id: int, update: Update):
    sh_cart.delete_one({"user_id": user_id})
    await update.callback_query.edit_message_text(text='Ваша корзина очищена!',
                                                  reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                                                      text='Вернутся к выбору',
                                                      switch_inline_query_current_chat=''
                                                  )]]))


async def red_order(user_id: int, update: Update):
    cart = sh_cart.find_one({"user_id": user_id})['order_items']
    cart_dishes = []
    for resident in cart:
        for dish in cart[resident]:
            cart_dishes.append(
                [(InlineKeyboardButton(
                    text=dish,
                    callback_data=','.join(['SRD', resident, dish])
                ))]
            )
    cart_dishes.append(
        [(InlineKeyboardButton(text='◀️Назад', callback_data='red_order'))]
    )
    await update.callback_query.edit_message_text(
        text='Выберете позицию которую хотите изменить:',
        reply_markup=InlineKeyboardMarkup(cart_dishes)
    )


async def show_red_dish(resident: str, dish: str, user_id: int,  update: Update):
    dish_data = get_one_dish(resident, dish)
    msg = '{}\n' \
          'Вес: {}\n' \
          'Цена: {} р.\n' \
          '<a href="{}">.</a>'.format(dish, dish_data['Вес'], dish_data['Цена'], dish_data['IMG'])
    rez1 = InlineKeyboardButton(callback_data=','.join(['add',
                                                        resident, dish, str(dish_data['Цена'])]),
                                text='{} ➕ Добавить в корзину'.format(
                                    get_dish_quantity(user_id=user_id, resident=resident, dish=dish)
                                ))
    rez2 = InlineKeyboardButton(callback_data='cart',
                                text='◀️Назад')
    rez3 = InlineKeyboardButton(callback_data=','.join(['minus', resident, dish, str(dish_data['Цена'])]),
                                text='➖ Удалить')
    keyboard = InlineKeyboardMarkup([[rez1, rez3], [rez2]])
    await update.callback_query.edit_message_text(
        text=msg,
        reply_markup=keyboard,
        disable_web_page_preview=False,
        parse_mode='HTML')
