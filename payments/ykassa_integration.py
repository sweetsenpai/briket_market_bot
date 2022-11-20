from telegram import Update
from yookassa import Configuration, Payment
from yookassa.domain.models.currency import Currency
from yookassa.domain.models.receipt import Receipt
from yookassa.domain.models.receipt_item import ReceiptItem
from yookassa.domain.common.confirmation_type import ConfirmationType
from yookassa.domain.request.payment_request_builder import PaymentRequestBuilder
from time import sleep
from briket_DB.passwords import yookassa_key
Configuration.account_id = '948782'
Configuration.secret_key = yookassa_key


async def chek_payment(payement_id: str, update: Update):
    timer = 1800
    while timer > 0:
        if Payment.find_one(payment_id=payement_id).status == 'succeeded':
            await update.message.reply_text(text='Ваш заказ успешно оплачен!')
            return True
        sleep(15)
        timer -= 15
    await update.message.reply_text(text='Ссылка для оплаты устарела, оформите заказ снова.')
    return False


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
    payment_url = 'Ваш заказ можно оплатить по этой ссылке:\n{}\n Ссылка будет действительна в течении 30 минут.'\
        .format(res.confirmation.confirmation_url)
    await update.message.reply_text(text=payment_url)
    if await chek_payment(payement_id=res.id, update=update) is True:
        return True
    return False





