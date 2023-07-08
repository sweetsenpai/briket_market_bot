from briket_DB.config import db
from briket_DB.sql_main_files.models import Workers, WorkertSchema


def create(worker_id, resident_chat_id):

    worker = {'worker_id': worker_id, 'resident_name': resident_chat_id}
    schema = WorkertSchema()
    new_resident = schema.load(worker, session=db.session)
    db.session.add(new_resident)
    db.session.commit()
    return schema.dump(new_resident), 201


def find_by_resident_id(resident_id):
    workers = Workers.query.filter(Workers.resident_name == resident_id).all()
    worker_list = []
    for worker in workers:
        print(worker.worker_id)
        worker_list.append(worker.worker_id)
    if not worker_list:
        return False
    return worker_list


