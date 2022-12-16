import os
from briket_DB.config import db
from briket_DB.sql_main_files.models import Customer, Resident

RESIDENTS = [{
    "resident_name": 'KFC',
    "chat_id": 352354383,
    "resident_addres": 'EKB',
    "resident_phone": '+78123743122',
    "resident_email": 'kfc@gmail.com',
    "description": 'Хорошо всем известная  курица',
    "img_url": str('https://upload.wikimedia.org/wikipedia/sco/thumb/b/bf/KFC_logo.svg/1200px-KFC_logo.svg.png')
},
    {
        "resident_name": 'Вкусно и точка',
        "chat_id": 352354383,
        "resident_addres": 'New-York',
        "resident_phone": '+78123744444',
        "resident_email": 'macdonalds@bk.ru',
        "description": 'Раньше было лучше',
        "img_url": str('https://upload.wikimedia.org/wikipedia/commons/c/cc/%D0%92%D0%BA%D1%83%D1%81%D0%BD%D0%BE_%E2%80%94_%D0%B8_%D1%82%D0%BE%D1%87%D0%BA%D0%B0.jpg')
    },
    {
        "resident_name": 'Мурмяу',
        "chat_id": 352354383,
        "resident_addres": 'New-York',
        "resident_phone": '+79042163341',
        "resident_email": 'macdonalds@bk.ru',
        "description": 'Это тест',
        "img_url": str(
            'http://res.cloudinary.com/dwexszkh4/image/upload/v1669732790/ifm6qs4hssyq0ciovfdm.jpg')
    }
]

CUSTOMER = [
    {'chat_id': 1, 'phone': '+79118468177', 'name': 'Александр', 'addres': 'SPB', 'email': '123@bk.com'},
    {'chat_id': 2, 'phone': '+79118468667', 'name': 'Даша', 'addres': 'MSK', 'email': 'test@bk.com'}
]

if os.path.exists('briket.db'):
    pass
else:
    db.create_all()

    for resident in RESIDENTS:
        r = Resident(
            resident_name=resident.get('resident_name'),
            chat_id=resident.get('chat_id'),
            resident_addres=resident.get('resident_addres'),
            resident_phone=resident.get('resident_phone'),
            resident_email=resident.get('resident_email'),
            description=resident.get('description'),
            img_url=resident.get('img_url')
        )
        db.session.add(r)

    for customer in CUSTOMER:
        c = Customer(chat_id=customer['chat_id'],
                     phone=customer['phone'],
                     name=customer['name'],
                     addres=customer['addres'],
                     email=customer['email'])
        db.session.add(c)

    db.session.commit()

