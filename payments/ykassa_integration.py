from telegram import Update
from briket_DB.shopping.shcart_db import sh_cart
from briket_DB.shopping.order_db import push_order
from yookassa import Configuration, Payment
from yookassa.domain.models.currency import Currency
from yookassa.domain.models.receipt import Receipt
from yookassa.domain.models.receipt_item import ReceiptItem
from yookassa.domain.common.confirmation_type import ConfirmationType
from yookassa.domain.request.payment_request_builder import PaymentRequestBuilder
from briket_DB.passwords import yookassa_key
from telegram.ext import ContextTypes
from datetime import datetime
Configuration.account_id = '948782'
Configuration.secret_key = yookassa_key


async def create_payment(user_id, update: Update, delivery_type):
    order = sh_cart.find_one({'user_id': user_id})
    receipt = Receipt()
    receipt.customer = {"phone": "", "email": "test@mail.ru"}
    receipt.tax_system_code = 1
    receipt.items = []
    for resident in order['order_items']:
        for dish in order['order_items'][resident]:
            receipt.items.append(
                ReceiptItem({
                    "description": dish,
                    "quantity": order['order_items'][resident][dish]['quantity'],
                    "amount": {
                        "value": order['order_items'][resident][dish]['price'],
                        "currency": Currency.RUB
                    },
                    "vat_code": 2
                })
            )
    order_num = datetime.now().microsecond
    builder = PaymentRequestBuilder()
    builder.set_amount({"value": order['total'], "currency": Currency.RUB}) \
        .set_confirmation({"type": ConfirmationType.REDIRECT, "return_url": "https://t.me/briket_test_bot"}) \
        .set_capture('waiting_for_capture ') \
        .set_description(f"Заказ №{order_num}") \
        .set_metadata({"orderNumber": order_num}) \
        .set_receipt(receipt)
    request = builder.build()
    res = Payment.create(request)
    payment_url = 'Ваш заказ можно оплатить по этой ссылке:\n{}\n Ссылка будет действительна в течении 15 минут.'\
        .format(res.confirmation.confirmation_url)
    await update.message.reply_text(text=payment_url)
    sh_cart.find_one_and_update(filter={"user_id": order['user_id']},
                                              update={'$set': {"payment_id": res.id}})
    sh_cart.find_one_and_update(filter={"user_id": order['user_id']},
                                update={'$set': {"payment_time": datetime.now()}})
    sh_cart.find_one_and_update(filter={"user_id": order['user_id']},
                                update={'$set': {"order_num": order_num}})
    sh_cart.find_one_and_update(filter={"user_id": order['user_id']},
                                update={'$set': {"delivery_type": delivery_type}})
    return False


async def payment_finder(context: ContextTypes.DEFAULT_TYPE):
    payments = sh_cart.find(filter={"payment_time": {'$exists': True}})
    if payments is None:
        return
    for payment in payments:
        if Payment.find_one(payment_id=payment['payment_id']).status == 'succeeded':
            await context.bot.sendMessage(chat_id=payment['user_id'], text='Ваш заказ успешно оплачен!')
            await push_order(user_id=payment['user_id'], context=context)
            return
        if (datetime.now() - payment['payment_time']).total_seconds() >= 900 or \
                datetime.time(payment['payment_time']).hour >= 20 :
            await context.bot.sendMessage(chat_id=payment['user_id'], text='Ссылка для оплаты устарела, оформите заказ снова.')
            sh_cart.find_one_and_update(filter={"user_id": payment['user_id']},
                                        update={'$unset': {"payment_id": ''}})
            sh_cart.find_one_and_update(filter={"user_id": payment['user_id']},
                                        update={'$unset': {"payment_time": datetime.now()}})
            return


x = sh_cart.find_one(filter={'user_id':352354383})

