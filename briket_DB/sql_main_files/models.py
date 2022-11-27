from briket_DB.config import db, ma


class Customer(db.Model):
    __tablename__ = 'customers'
    customer_id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, index=True)
    phone = db.Column(db.String(32))
    name = db.Column(db.String(32))
    addres = db.Column(db.String(32))
    disc_status = db.Column(db.Boolean)


class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
        sqla_session = db.session
        load_instance = True


class Resident(db.Model):
    __tablename__ = 'residents'
    resident_id = db.Column(db.Integer, primary_key=True)
    resident_name = db.Column(db.String(32))
    chat_id = db.Column(db.Integer, index=True)
    resident_addres = db.Column(db.String(32))
    resident_phone = db.Column(db.String(32))
    resident_email = db.Column(db.String(32))
    description = db.Column(db.String(32))
    img_url = db.Column(db.Text())


class ResidentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Resident
        sqla_session = db.session
        load_instance = True
