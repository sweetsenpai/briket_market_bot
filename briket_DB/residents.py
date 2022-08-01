from flask import make_response, abort
from briket_DB.config import db
from briket_DB.models import Resident, ResidentSchema


def read_all():
    resident = Resident.query.order_by(Resident.resident_id).all()
    resident_schema = ResidentSchema(many=True)
    return resident_schema.dump(resident)


def read_one(resident_id):
    resident = Resident.query.filter(Resident.resident_id == resident_id).one_or_none()
    if resident is not None:
        resident_schema = ResidentSchema()
        return resident_schema.dump(resident)
    else:
        abort(
            404,
            "Resident not found for {} ID".format(resident_id)
        )


def create(resident):
    phone = resident.get('resident_phone')
    ex_resident = Resident.query.filter(Resident.resident_phone == phone).one_or_none()
    if ex_resident is None:
        schema = ResidentSchema()
        new_resident = schema.load(resident, session=db.session)
        db.session.add(new_resident)
        db.session.commit()
        return schema.dump(new_resident), 201
    else:
        abort(409, 'Resident with phone nymber: {} exist allredy'.format(phone))


def update(resident_id, resident):
    update_resident = Resident.query.filter(Resident.resident_id == resident_id).one_or_none()

    if update_resident is None:
        abort(
            404,
            "Resident not found for id {}".format(resident_id)
        )
    else:
        schema = ResidentSchema()
        update = schema.load(resident, session=db.session)
        update.resident_id = update_resident.resident_id

        db.session.merge(update)
        db.session.commit()

        data = schema.dump(update_resident)
        return data, 200


def delete(resident_id):
    resident = Resident.query.filter(Resident.resident_id == resident_id).one_or_none()
    if resident is not None:
        db.session.delete(resident)
        db.session.commit()
        return make_response("Resident {} deleted".format(resident_id), 200)
    else:
        abort(
            404,
            "Resident not found by id {}".format(resident_id)
        )
