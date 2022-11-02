from briket_DB.order_db import orders_db
from briket_DB.residents import read_all
from datetime import datetime


def get_resident_report_month(resident_name: str):
    msg = f'<b>{resident_name}</b>\n'
    comission = 0
    for order in orders_db.find({'$and': [{f'order_items.{resident_name}': {'$exists': True}},
                                          {f'order_items.{resident_name}.status': 'Готов'}]}):
        if datetime.date(order['time']).strftime('%Y %m') == datetime(year=2022, month=9, day=15).strftime('%Y %m'):
            msg += 'Номер заказа:' + str(order['order_num'])+'\n' + order['delivery_type']+'\n'
            sub_sum = sub_total(order_num=order['order_num'], resident_name=resident_name)
            if order['delivery_type'] == 'Самовывоз':
                msg += f'Сумма заказа:{sub_sum}\nКомиссия:{round(sub_sum*0.1)}\n'
                msg += '----------------------\n'
                comission += round(sub_sum*0.1)
            elif order['delivery_type'] == 'Доставка':
                msg += f'Сумма заказа:{sub_sum}\nКомиссия:{round(sub_sum * 0.2)}\n'
                msg += '----------------------\n'
                comission += round(sub_sum * 0.2)
    msg += f'<b>Комиссия за месяц:{comission}₽</b>'
    return msg


def get_resident_report_day(resident_name):
    comission = 0
    msg = f'<b>{resident_name}</b>\n'
    for order in orders_db.find({'$and': [{f'order_items.{resident_name}': {'$exists': True}},
                                          {f'order_items.{resident_name}.status': 'Готов'}]}):
        if datetime.date(order['time']).strftime('%Y %m %d') == datetime.now().strftime('%Y %m %d'):
            msg += 'Номер заказа:' + str(order['order_num'])+'\n' + order['delivery_type']+'\n' + datetime.date(order['time']).strftime('%Y %m %d')
            sub_sum = sub_total(order_num=order['order_num'], resident_name=resident_name)
            if order['delivery_type'] == 'Самовывоз':
                msg += f'<i>Сумма заказа:{sub_sum}\nКомиссия:{round(sub_sum*0.1)}</i>\n'
                msg += '----------------------\n'
                comission += round(sub_sum*0.1)
            elif order['delivery_type'] == 'Доставка':
                msg += f'<i>Сумма заказа:{sub_sum}\nКомиссия:{round(sub_sum * 0.2)}</i>\n'
                msg += '----------------------\n'
                comission += round(sub_sum * 0.2)
    msg += f'<b>Комиссия за день:{comission}₽</b>'
    return msg


def sub_total(order_num, resident_name):
    sub_sum = 0
    order = orders_db.find_one({'order_num': order_num})['order_items'][resident_name]
    for dish in order.keys():
        try:
            sub_sum += float(order[dish]['price']) * order[dish]['quantity']
        except TypeError:
            continue
    return sub_sum


