import os
from briket_DB.config import db
from briket_DB.models import Customer, Resident

RESIDENTS = [{
    "resident_name": 'KFC',
    "chat_id": 1337,
    "resident_addres": 'EKB',
    "resident_phone": '+78123743122',
    "resident_email": 'kfc@gmail.com',
    "description": 'Хорошо всем известная не вкусная курица'
},
    {
        "resident_name": 'Вкусно и точка',
        "chat_id": 1488,
        "resident_addres": 'New-York',
        "resident_phone": '+78123744444',
        "resident_email": 'macdonalds@bk.ru',
        "description": 'Стыд и срам'
    },
    {
        "resident_name": 'Burger King',
        "chat_id": 1222,
        "resident_addres": 'OMSK',
        "resident_phone": '+71111111',
        "resident_email": 'bk@bk.ru',
        "description": 'Отличное место'
    }
]

CUSTOMER = [
    {'chat_id': 1, 'phone': '+79118468177', 'addres': 'SPB', 'disc_status': True},
    {'chat_id': 2, 'phone': '+79232556679', 'addres': 'MSK', 'disc_status': False}
]

if os.path.exists('briket.db'):
    os.remove('briket.db')

db.create_all()

for resident in RESIDENTS:
    r = Resident(
        resident_name=resident.get('resident_name'),
        chat_id=resident.get('chat_id'),
        resident_addres=resident.get('resident_addres'),
        resident_phone=resident.get('resident_phone'),
        resident_email=resident.get('resident_email'),
        description=resident.get('description')
    )
    db.session.add(r)

for customer in CUSTOMER:
    c = Customer(chat_id=customer['chat_id'],
                 phone=customer['phone'],
                 addres=customer['addres'],
                 disc_status=customer['disc_status'])
    db.session.add(c)

db.session.commit()