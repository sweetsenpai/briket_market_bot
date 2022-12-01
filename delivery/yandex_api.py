import requests as re

from uuid import uuid4
import telegram.error
from briket_DB.sql_main_files.customers import find_user_by_id
from briket_DB.passwords import yandex_key
from briket_DB.config import mongodb
from datetime import datetime
from telegram.ext import ContextTypes
orders_db = mongodb.orders
admins = mongodb.admin
default_addres = 'Москва, бульв. Новинский, д. 8, стр. 1'
custom_head = {'Authorization': f'Bearer {yandex_key}', 'Accept-Language': 'ru/ru'}


def send_delivery_order(order):
    customer = find_user_by_id(order['user_id'])
    delivery_req = {
        # Требования к доставке
        "client_requirements": {
            "assign_robot": False,
            "pro_courier": False,
            "taxi_class": "express",
            "cargo_options": ["thermobag"],
        },
        "items": [
            {
                "cost_currency": "RUB",
                "cost_value": "0.00",
                "droppof_point": 2,
                "pickup_point": 1,
                "quantity": 1,
                "title": "Горячая еда"
            }
        ],
        "optional_return": True,
        "route_points": [
            # Адрес ресторана
            {
                "address": {
                    #        "coordinates": [37.587093, 55.733974],
                    "city": "Москва",
                    "country": "Российская Федерация",
                    "description": "Москва, Россия",
                    "fullname": f"Москва, {default_addres}",
                },
                # Контакты отправителя
                "contact": {
                    "email": "morty@yandex.ru",
                    "name": "Кто-ты?",
                    "phone": "+79101234567"
                },
                "external_order_cost": {
                    "currency": "RUB",
                    "currency_sign": "₽",
                    "value": "100.0"
                },
                "external_order_id": str(order['order_num']),
                "point_id": 1,
                "skip_confirmation": False,
                "type": "source",
                "visit_order": 1
            },
            # Адрес клиента
            {
                "address": {
                    "city": "Москва",
                    "comment": order['delivery']['comment'],
                    "country": "Российская Федерация",
                    "description": "Москва, Россия",
                    "fullname": f"Москва, {order['delivery']['addres']}",

                },
                # Контакты получателя
                "contact": {
                    "name": f"{customer['name']}",
                    "phone": f"{customer['phone']}"
                },
                "external_order_cost": {
                    "currency": "RUB",
                    "currency_sign": "₽",
                    "value": "1.0"
                },
                "external_order_id": str(order['order_num']),
                "point_id": 2,
                "skip_confirmation": False,
                "type": "destination",
                "visit_order": 2
            }
        ],
        "skip_act": False,
        "skip_client_notify": False,
        "skip_door_to_door": False,
        "skip_emergency_notify": True
    }
    random_call = uuid4()
    call = re.post(url=f'https://b2b.taxi.yandex.net/b2b/cargo/integration/v2/claims/create?request_id={random_call}',
                   headers=custom_head, json=delivery_req)
    if call.status_code != 200:
        print(call.json())
        return False
    return call.json()['id']


def driver_info(claim_id):
    try:
        call = re.post(url='https://b2b.taxi.yandex.net/b2b/cargo/integration/v2/driver-voiceforwarding', headers=custom_head,
                   json=claim_id, timeout=30)
        if call.status_code != 200:
            return False
        return '{}\nдоб. номер:{}'.format(call.json()['phone'], call.json()['ext'])
    except re.exceptions.RequestException:
        return False


def delivery_range(delivery_addres):
    req = {
        "client_requirements": {
            "assign_robot": False,
            "cargo_options": ["thermobag", "express"],
            "pro_courier": False,
            "taxi_class": "express"
        },
        "route_points": [
            {"fullname": "Москва, бульв. Новинский, д. 8, стр. 1"},
            {"fullname": "Москва,"+delivery_addres}],
        "skip_door_to_door": False
    }
    call = re.post(url='https://b2b.taxi.yandex.net/b2b/cargo/integration/v1/check-price', headers=custom_head,
                   json=req)
    if call.status_code != 200:
        return False, 'Вы указали некорректный адрес'
    if call.json()['distance_meters'] > 3500:
        return False, 'Адрес находится вне зоны доставки'
    return True, call.json()['distance_meters']


async def driver_number_sender(context: ContextTypes.DEFAULT_TYPE):
    orders_driver = orders_db.find({'$and': [{'delivery.driver_number': {'$exists': False}},
                                    {'delivery_type': 'Доставка'}]})
    if orders_driver is None:
        return

    for order in orders_driver:
        print(order)
        if order['user_id'] == 352354383:
            return
        if datetime.date(order['time']).strftime('%Y %m %d') == datetime.now().strftime('%Y %m %d'):
            driver_phone = driver_info(order['delivery']['id'])
            print(driver_phone)
            if driver_phone is not False:
                orders_db.find_one_and_update(filter={"user_id": order['user_id']},
                                              update={'$set': {"delivery.driver_number": driver_phone}})
                for admin in admins.find():
                    try:
                        context.bot.sendMessage(text='Заказ №:{}\n'
                                                     'Назначен курьер!\n'
                                                     'Контактный номер:{}'.format((order['order_num']), driver_phone),
                                                chat_id=admin['chat_id'])
                    except KeyError or telegram.error.BadRequest:
                        continue
    return

