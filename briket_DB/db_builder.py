import os
from config import db
from briket_DB.customer_model import Customer

CUSTOMER = [
    {'chat_id': 1, 'phone': '+79118468177', 'addres': 'SPB', 'disc_status': True},
    {'chat_id': 2, 'phone': '+79232556679', 'addres': 'MSK', 'disc_status': False}
]

if os.path.exists('customers.db'):
    os.remove('customers.db')

db.create_all()

for customer in CUSTOMER:
    c = Customer(chat_id=customer['chat_id'], phone=customer['phone'], addres=customer['addres'], disc_status=customer['disc_status'])
    db.session.add(c)

db.session.commit()
