from briket_DB.config import db, ma
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field


class Customer(db.Model):
    __tablename__ = 'customers'
    customer_id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, index=True)
    phone = db.Column(db.String(32))
    addres = db.Column(db.String(32))
    disc_status = db.Column(db.Boolean)


class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
        sqla_session = db.session
        load_instance = True


