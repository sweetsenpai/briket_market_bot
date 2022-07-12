from flask import make_response, abort, jsonify
from briket_DB.config import db
from briket_DB.customer_model import Customer, CustomerSchema
import json


def read_all():
    customer = Customer.query.order_by(Customer.customer_id).all()
    customer_schema = CustomerSchema(many=True)
    return customer_schema.dump(customer)


def read_one(customer_id):
    customer = Customer.query.filter(Customer.customer_id == customer_id).one_or_none()
    if customer is not None:
        customer_schema = CustomerSchema()
        return customer_schema.dump(customer)
    else:
        abort(
            404,
            "Customer not found for {} ID".format(customer_id)
        )


def create(customer):
    chat_id = customer.get('chat_id')
    phone = customer.get('phone')
    addres = customer.get('addres')
    disc_status = customer.get('disc_status')

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
    chat_id = customer.get('chat_id')
    phone = customer.get('phone')
    addres = customer.get('addres')
    disc_status = customer.get('disc_status')
    existing_customer = Customer.query.filter(Customer.phone == phone).filter(Customer.chat_id == chat_id).one_or_none()

    if update_customer is None:
        abort(
            404,
            "Customer not found for id {}".format(customer_id)
        )
    elif (
      existing_customer is not None and existing_customer.customer_id != customer_id
    ):
        abort(
            409,
            "Customer with chat_id {} and phone {}".format(chat_id, phone)
        )
    else:
        schema = CustomerSchema()
        update = schema.load(customer, session=db.session)
        update.customer_id = update_customer.customer_id

        db.session.merge(update)
        db.session.commit()

        data = schema.dump(update_customer)
        return data, 200


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

