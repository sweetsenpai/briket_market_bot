# shopId 948782
# test_0GfUYI52S7AAEGObdI8PgnlSXqgM3T-jSQtOo0BjNNE
from yookassa import Configuration, Payment
from yookassa.domain.models.currency import Currency
from yookassa.domain.models.receipt import Receipt
from yookassa.domain.models.receipt_item import ReceiptItem
from yookassa.domain.common.confirmation_type import ConfirmationType
from yookassa.domain.request.payment_request_builder import PaymentRequestBuilder
Configuration.account_id = '948782'
Configuration.secret_key = 'test_0GfUYI52S7AAEGObdI8PgnlSXqgM3T-jSQtOo0BjNNE'
from briket_DB.shcart_db import sh_cart


def create_payment(order, order_num:int):
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
    text = 'Ваш заказ можно оплатить по этой ссылке:\n{}'.format(res.confirmation.confirmation_url)
    return res







