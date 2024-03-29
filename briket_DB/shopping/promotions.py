from briket_DB.config import mongodb
import random
import string
from briket_DB.shopping.shcart_db import sh_cart
sales_db = mongodb.promotions


def generate_personal_code(user_id):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(6))
    personal_code = {
        'code': result_str,
        'description': '',
        'ammount': 0,
        'procent': 20,
        'one_time': True,
        'start_price': 500,
        'uses': [''],
        'user_id': user_id
    }
    sales_db.insert_one(personal_code)
    return result_str


def chek_personal_code(user_id):
    pr_code = sales_db.find_one({'user_id': user_id})
    if pr_code is None:
        return generate_personal_code(user_id)
    return pr_code['code']


def start_sale(text='', ammount=0, promo_code='', procent=0, one_time=False, start_price=0,master=0):
    sale = {
        'code': promo_code,
        'master': master,
        'description': text,
        'ammount': ammount,
        'procent': procent,
        'one_time': one_time,
        'start_price': start_price,
        'uses': [''],
    }
    sales_db.insert_one(sale)
    return


def chek_one_time_promo(promo, user_id):
    if user_id in promo['uses']:
        return False
    sales_db.find_one_and_update(filter=promo, update={'$push': {'uses': user_id}})
    return True


def chek_start_price(promo, user_id):
    cart_total = 50
    if promo['start_price'] > cart_total:
        return False, promo['start_price'] - cart_total
    return True


def chek_promo(promo_code, user_id):
    promo = sales_db.find_one({'code': promo_code})
    if promo is None:
        return 'Промокод не найден. Чтобы попробовать ещё раз нажмите <Да>  на клавиатуре', False

    if add_promo_cart(promo=promo_code, user_id=user_id) is False:
        return 'Можно использовать только один промокод .'

    if chek_start_price(promo=promo, user_id=user_id) is False:
        ammount = chek_start_price(promo=promo, user_id=user_id)[1]
        sh_cart.find_one_and_update(filter={'user_id': user_id},
                                    update={'$unset': {'promo_code': True}})
        return 'Необходимо заказать ещё на {}р. чтобы активировать промокод.'.format(
            ammount), False

    if promo['one_time'] is True:
        if chek_one_time_promo(promo=promo, user_id=user_id) is False:
            sh_cart.find_one_and_update(filter={'user_id': user_id},
                                        update={'$unset': {'promo_code': True}})
            return 'Промокод уже использован', False

    if promo['ammount'] != 0:
        return 'Скидка в {} руб. будет применена к твоему заказу.'.format(promo['ammount']), True

    return 'Скидка в {}%. будет применена к твоему заказу.'.format(promo['procent']), True


def add_promo_cart(promo: str, user_id: int):
    cart = sh_cart.find_one({'user_id': user_id})
    if cart is None:
        sh_cart.insert_one({'user_id': user_id, 'promo_code': promo})
        return True
    try:
        if cart['promo_code'] is True:
            return False
    except KeyError:
        sh_cart.find_one_and_update(filter=cart, update={'$set': {'promo_code': promo}})
        return True


def apply_promo(user_id: int):
    cart = sh_cart.find_one({'user_id': user_id})
    try:
        promo = sales_db.find_one({'code': cart['promo_code']})
    except KeyError:
        return
    if promo['ammount'] == 0:
        total = (float(cart['total'])/100) * (100 - promo['procent'])
        sh_cart.find_one_and_update(filter=cart, update={'$set': {'total': round(total, 2)}})
        return
    sh_cart.find_one_and_update(filter=cart, update={'$set': {'total': round(cart['total'] - promo['ammount'], 2)}})
    return


def stop_promo(code_word: str):
    sales_db.delete_one({'code': code_word})
    return 'Промокод успешно удален.'


def output_promotions(promotion):
    if promotion['ammount'] == 0:
        text = '{} - {}%'.format(promotion['code'], promotion['procent'])
        return text
    text = '{} - {}р.'.format(promotion['code'], promotion['ammount'])
    return text


