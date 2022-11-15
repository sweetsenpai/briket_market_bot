import requests as re
from uuid import uuid4
from briket_DB.order_db import orders_db
from briket_DB.customers import read_one
from briket_DB.passwords import yandex_key

default_addres = 'Москва, бульв. Новинский, д. 8, стр. 1'
custom_head = {'Authorization': f'Bearer {yandex_key}', 'Accept-Language': 'ru/ru'}


# default_addres
# contacts
# Подтверждение заказа


def send_delivery_order(user_id, order_num):
    order = orders_db.find_one({'order_num': order_num})
    customer = read_one(user_id)
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
                "external_order_id": order_num,
                "point_id": 1,
                "skip_confirmation": False,
                "type": "source",
                "visit_order": 1
            },
            # Адрес клиента
            {
                "address": {
                    "city": "Москва",
                    "comment": order['comments'],
                    "country": "Российская Федерация",
                    "description": "Москва, Россия",
                    "fullname": f"Москва, {order['addres']}",
                },
                # Контакты получателя
                "contact": {
                    "email": "morty@yandex.ru",
                    "name": "Кто-я?",
                    "phone": f"{customer['phone']}"
                },
                "external_order_cost": {
                    "currency": "RUB",
                    "currency_sign": "₽",
                    "value": "1.0"
                },
                "external_order_id": order_num,
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
        return False
    return call.json()


def driver_info(claim_id):
    call = re.post(url='b2b.taxi.yandex.net/b2b/cargo/integration/v2/driver-voiceforwarding', headers=custom_head,
                   json=claim_id)
    if call.status_code != 200:
        return False
    return call.json()['phone']


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
            {"fullname": delivery_addres}],
        "skip_door_to_door": False
    }
    call = re.post(url='https://b2b.taxi.yandex.net/b2b/cargo/integration/v1/check-price', headers=custom_head,
                   json=req)
    if call.status_code != 200:
        return False
    if call.json()['distance_meters'] > 3500:
        return 'Адрес находится за зоной доставки'
    return True, call.json()['distance_meters']


