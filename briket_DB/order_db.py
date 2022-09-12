from briket_DB.config import mongodb
from datetime import datetime
from briket_DB.residents import get_chat_id

orders_db = mongodb.orders
sh_cart = mongodb.sh_cart


async def push_order(user_id: int, context):
    cart = sh_cart.find_one({"user_id": user_id})
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    del cart['_id']
    cart['time'] = time
    cart['status'] = 'new'
    cart['order_num'] = datetime.now().microsecond
    orders_db.insert_one(cart)
#    sh_cart.delete_one({"user_id": user_id})
    await send_order_residents(cart['order_num'], context)
    return


async def send_order_residents(order_num: int, context):
    full_order = orders_db.find_one({"order_num": order_num})
    for resident in full_order['order_items']:
        resident_order = 'Заказ №{}\n'.format(full_order['order_num'])
        for dish in full_order['order_items'][resident]:
            resident_order += '{}: {}\n'.format(dish, full_order['order_items'][resident][dish]['quantity'])
        await context.bot.sendMessage(text=resident_order, chat_id=get_chat_id(resident))
    return




