from flask import make_response, abort
from briket_DB.config import db
from briket_DB.sql_main_files.models import Customer, CustomerSchema
import json


def read_all():
    customer = Customer.query.order_by(Customer.customer_id).all()
    customer_schema = CustomerSchema(many=True)
    return customer_schema.dump(customer)


def read_one(customer_id):
    customer = Customer.query.filter(Customer.chat_id == customer_id).one_or_none()
    if customer is not None:
        customer_schema = CustomerSchema()
        return customer_schema.dump(customer)
    else:
        return False


def find_id(chat_id):
    customer = Customer.query.filter(Customer.chat_id == chat_id).one_or_none()
    if customer is not None:
        customer_schema = CustomerSchema()
        return customer_schema.dump(customer)
    else:
        return None


def create(customer):
    chat_id = customer.get('chat_id')
    ex_customer = Customer.query.filter(Customer.chat_id == chat_id).one_or_none()

    if ex_customer is None:
        schema = CustomerSchema()
        new_customer = schema.load(customer, session= db.session)
        db.session.add(new_customer)
        db.session.commit()
        return schema.dump(new_customer), 201
    else:
        abort(409, 'Customer with chat_id {} exist allredy'.format(chat_id))


def update(customer_id, customer):
    update_customer = Customer.query.filter(Customer.customer_id == customer_id).one_or_none()
    if update_customer is None:
        abort(
            404,
            "Customer not found for id {}".format(customer_id)
        )
    else:
        schema = CustomerSchema()
        update_data = schema.load(customer, session=db.session)
        update_data.customer_id = update_customer.customer_id

        db.session.merge(update_data)
        db.session.commit()

        data = schema.dump(update_customer)
        return data, 200


def inser_new_name(chat_id, name):
    update_customer = Customer.query.filter(Customer.chat_id == chat_id).one_or_none()
    if update_customer is None:
        abort(
            404,
            "Customer not found for id {}".format(chat_id)
        )
    else:
        update_customer.name = name
        db.session.commit()
        return 200


def insert_new_email(chat_id, email):
    update_customer = Customer.query.filter(Customer.chat_id == chat_id).one_or_none()
    if update_customer is None:
        abort(
            404,
            "Customer not found for id {}".format(chat_id)
        )
    else:
        update_customer.email = email
        db.session.commit()
        return 200


def delete(customer_id):
    customer = Customer.query.filter(Customer.customer_id == customer_id).one_or_none()
    if customer is not None:
        db.session.delete(customer)
        db.session.commit()
        return make_response("Customer {} deleted".format(customer_id), 200)
    else:
        abort(
            404,
            "Customer not found by id {}".format(customer_id)
        )


def find_user_by_id(user_id):
    customer = Customer.query.filter(Customer.chat_id == user_id).one_or_none()
    if customer is not None:
        customer_schema = CustomerSchema()
        return customer_schema.dump(customer)
    else:
        return None


def insert_new_addres(chat_id: int, addres):
    update_customer = Customer.query.filter(Customer.chat_id == chat_id).one_or_none()
    if update_customer is None:
        abort(
            404,
            "Customer not found for chat_id {}".format(chat_id)
        )
    else:
        try:
            address_list = list(json.loads(update_customer.addres))
            address_list.append(addres)
            update_customer.addres = json.dumps(address_list)
            db.session.commit()
            return 200
        except:
            update_customer.addres = json.dumps([addres])
            db.session.commit()


def addres_keyboard(chat_id: int):
    update_customer = Customer.query.filter(Customer.chat_id == chat_id).one_or_none()
    if update_customer is None:
        abort(
            404,
            "Customer not found for chat_id {}".format(chat_id)
        )
    else:
        try:
            return json.loads(update_customer.addres)
        except json.decoder.JSONDecodeError:
            return update_customer.addres


def delete_addres(chat_id: int, del_addres):
    customer = Customer.query.filter(Customer.chat_id == chat_id).one_or_none()
    if customer is None:
        abort(
            404,
            "Customer not found for chat_id {}".format(chat_id)
        )
    else:

        adreses = list(json.loads(customer.addres))
        adreses.remove(del_addres)
        print(adreses)
        customer.addres = json.dumps(adreses)
        db.session.commit()
        return 200


def find_customer_by_phone(phone):
    customer = Customer.query.filter(Customer.phone == phone).one_or_none()
    if customer is not None:
        customer_schema = CustomerSchema()
        return customer_schema.dump(customer)
    else:
        return None


