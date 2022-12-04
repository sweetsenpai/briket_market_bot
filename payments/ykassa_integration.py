from telegram import Update
from briket_DB.shopping.shcart_db import sh_cart
import asyncio
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


async def chek_payment(payement_id: str, update: Update):
    loop = asyncio.get_running_loop()
    end_time = loop.time() + 900.0
    while True:
        if Payment.find_one(payment_id=payement_id).status == 'succeeded':
            await update.message.reply_text(text='Ваш заказ успешно оплачен!')
            return True
        if (loop.time() + 15.0) >= end_time:
            await update.message.reply_text(text='Ссылка для оплаты устарела, оформите заказ снова.')
            return False
        await asyncio.sleep(15)


async def create_payment(order, order_num: int, update: Update ):
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
                                              update={'$set': {"payment": res.id}})
    sh_cart.find_one_and_update(filter={"user_id": order['user_id']},
                                update={'$set': {"payment_time": datetime.now().time()}})
    return


async def payment_finder(context: ContextTypes.DEFAULT_TYPE):
    payments = sh_cart.find(filter={"payment_time":{'$exists': True}})
    if payments is None:
        return
#    for payment in payments:
#        chek_payment()


