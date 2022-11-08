from briket_DB.config import mongodb

reviews_db = mongodb.reviews


def insert_moderation_revie(user_name, user_id, resident_name, text):
    revie = {'user_name': user_name,
             'text': text}
    reviews_db.find_one_and_update(filter={'resident': resident_name},
                                   update={'$set': {f'on_moderation.{user_id}': revie}})
    return


def publish_revie(user_id, resident_name):
    text = reviews_db.find_one(filter={'resident': resident_name})['on_moderation'][str(user_id)]['text']
    reviews_db.find_one_and_update(filter={'resident': resident_name},
                                   update={'$unset': {f'on_moderation.{user_id}': ''}})
    reviews_db.find_one_and_update(filter={'resident': resident_name},
                                   update={'$push': {'published': text}})
    return


def read_revie(comment_num=0, resident_name='KFC'):
    try:
        comment = reviews_db.find_one(filter={'resident': resident_name})['published'][comment_num]
        return comment
    except IndexError or TypeError:
        return False


def update_text(user_id, text):
    reviews_db.find_one_and_update(filter={f'on_moderation.{user_id}.text': '...'},
                                   update={'$set': {f'on_moderation.{user_id}.text': text}})

    return


def get_resident(user_id, text):
    res = reviews_db.find_one({f'on_moderation.{user_id}.text': text})['resident']
    return res


