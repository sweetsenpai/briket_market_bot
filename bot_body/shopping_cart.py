import logging
from briket_DB.sql_main_files.residents import delet_on_phone
from briket_DB.config import mongodb
from briket_DB.shopping.previous_orders import show_po, repeat_order
from briket_DB.reviews.callback_reviews import show_review
from briket_DB.sql_main_files.customers import delete_addres, read_one
from bot_body.menu import dish_card_keyboard, inline_menu_generation, inline_generator, dish_card
from briket_DB.reviews.reviews_main import publish_revie, del_review
from briket_DB.shopping.shcart_db import (add_dish, remove_dish,
                                          show_cart, empty_shcart,
                                          red_order, show_red_dish)

from briket_DB.shopping.order_db import (client_info,
                                         tech_support, accept_order,
                                         decline_order, finish_order)
from telegram import (Update,
                      InlineKeyboardMarkup,
                      InlineKeyboardButton,constants)

from telegram.ext import ContextTypes
from text_integration.pastebin_integration import get_text_api
from briket_DB.shopping.promotions import stop_promo
from order_ofirm.callback_hend import make_order
from user.addresses import inline_addresses
from datetime import datetime
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def cart_inline():
    conf_order = InlineKeyboardButton(text='Оформить заказ', callback_data='make_order')
    redact_order = InlineKeyboardButton(text=get_text_api('XDHGv5uZ'), callback_data='red_order')
    empty_cart = InlineKeyboardButton(text=get_text_api('MguE3Kt7'), callback_data='empty_cart')
    back = InlineKeyboardButton(text=get_text_api('4Sj7fP4j'), switch_inline_query_current_chat='')
    res = InlineKeyboardMarkup([[conf_order, redact_order], [back, empty_cart]])
    return res


async def handle_invalid_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Informs the user that the button is no longer available."""
    await update.callback_query.answer("Прости, данные уже устарели😔 Вызови меню ещё раз.")
    return


async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clears the callback data cache"""
    context.bot.callback_data_cache.clear_callback_data()
    context.bot.callback_data_cache.clear_callback_queries()
    await update.effective_message.reply_text("All clear!")


async def cart_show_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text=show_cart(update.message.from_user.id),
                                    reply_markup=cart_inline())
    return


async def call_back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    cb_data = query.data.split(',')
    logger.info(
        "Callback data: {}".format(cb_data)
    )
    if cb_data[0] == 'add':
        add_dish(user_id=query.from_user.id, resident=cb_data[1], dish=cb_data[2], price=cb_data[3])
        await update.callback_query.edit_message_reply_markup(
            reply_markup=dish_card_keyboard(user_id=query.from_user.id, resident=cb_data[1], dish=cb_data[2],
                                            price=cb_data[3]))
        await query.answer()
        return
    elif cb_data[0] == 'minus':
        remove_dish(user_id=query.from_user.id, resident=cb_data[1], dish=cb_data[2])
        await update.callback_query.edit_message_reply_markup(
            reply_markup=dish_card_keyboard(user_id=query.from_user.id, resident=cb_data[1], dish=cb_data[2],
                                            price=cb_data[3]))
        await query.answer()
        return
    elif cb_data[0] == 'cart':
        await query.edit_message_text(text=show_cart(user_id=query.from_user.id),
                                      reply_markup=cart_inline())
        await query.answer()
        return
    elif cb_data[0] == 'red_order':
        await red_order(user_id=query.from_user.id, update=update)
        await query.answer()
        return
    elif cb_data[0] == 'SRD':
        await show_red_dish(resident=cb_data[1], dish=cb_data[2], user_id=query.from_user.id, update=update)
        await query.answer()
        return
    elif cb_data[0] == 'empty_cart':
        await empty_shcart(user_id=query.from_user.id, update=update)
        await query.answer()
        return
    elif cb_data[0] == 'accept':
        await accept_order(order_num=int(cb_data[1]), update=update, resident=cb_data[2])
        await query.answer()
        return
    elif cb_data[0] == 'decline_order':
        await decline_order(order_num=int(cb_data[1]), update=update, resident=cb_data[2])
        await query.answer()
    elif cb_data[0] == 'support':
        await tech_support(context=context, msg_chat=update.callback_query.from_user.id)
        await query.answer()
        return
    elif cb_data[0] == 'client':
        await client_info(order_num=int(cb_data[1]), context=context, msg_chat=update.callback_query.from_user.id)
        await query.answer()
        return
    elif cb_data[0] == 'finish_order':
        await finish_order(order_num=int(cb_data[1]), update=update, resident=cb_data[2], context=context)
        await query.answer()
        return
    elif cb_data[0] == 'del_resident':
        delet_on_phone(cb_data[1])
        await update.callback_query.edit_message_text(text='Резидент успешно удален!')
        return
    elif cb_data[0] == 'del_admin':
        mongodb.admin_db.delete_one({"phone": cb_data[1]})
        await update.callback_query.edit_message_text(text='Администратор успешно удален!')
        return
    elif cb_data[0] == 'del_promo':
        stop_promo(cb_data[1])
        await update.callback_query.edit_message_text(text='Акция успешно преостановлена!')
        return
    elif cb_data[0] == 'reviews':
        await show_review(update=update, resident_name=cb_data[1])
        return
    elif cb_data[0] == 'show_rev':
        await show_review(update=update, resident_name=cb_data[1], page=cb_data[2])
        return
    elif cb_data[0] == 'publish_rev':
        publish_revie(user_id=cb_data[1], resident_name=cb_data[2])
        await update.callback_query.edit_message_text(text='Отзыв успешно опубликован.')
        await context.bot.send_message(chat_id=cb_data[1], text='Ваш отзыв опубликован!')
        return
    elif cb_data[0] == 'delete_rev':
        del_review(user_id=cb_data[1], resident=cb_data[2])
        await update.callback_query.edit_message_text(text='Отзыв удален.')
        return
    elif cb_data[0] == 'make_order':
        if show_cart(user_id=update.callback_query.from_user.id) == 'Тут ничего нет':
            await update.callback_query.answer(text='В корзине ничего нет(', show_alert=True)
            return
        if read_one(update.callback_query.from_user.id) is False:
            await update.callback_query.answer(text='Для оформления заказа необходимо пройти регистрацию.\n'
                                                    'Это займет всего пару минут.', show_alert=True)
            return

        if datetime.now().weekday() == 6:
            if int(datetime.now().hour) >= 23 or int(datetime.now().hour) < 11:
                await update.callback_query.answer(text='График работы\n'
                                                        'Пн-Сб: с 10:00 до 22:00\n'
                                                        'Вск: c 11:00 до 23:00',
                                                   show_alert=True
                                                   )
                return
            else:
                await make_order(update, context)
                return
        else:
            if int(datetime.now().hour) >= 21 or int(datetime.now().hour) < 10:
                await update.callback_query.answer(text='График работы\n'
                                                        'Пн-Сб: с 10:00 до 22:00\n'
                                                        'Вск: c 11:00 до 23:00',
                                                   show_alert=True
                                                   )
                return
            else:
                await make_order(update, context)
                return

    elif cb_data[0] == 'get_menu':
        await update.callback_query.edit_message_text(text=dish_card(cb_data[1]), parse_mode=constants.ParseMode.HTML,
                                                      reply_markup=inline_menu_generation(cb_data[1]))
        return

    elif cb_data[0] == 'back_inline':
        await update.callback_query.edit_message_reply_markup(reply_markup=inline_generator(cb_data[1]))
        return
    elif cb_data[0] == 'remove_address':
        delete_addres(chat_id=update.callback_query.from_user.id, del_addres=cb_data[1])
        await update.callback_query.edit_message_text('Адрес успешно удален.',
                                                      reply_markup=inline_addresses(user_id=
                                                                                    update.callback_query.from_user.id))
    elif cb_data[0] == 'PO':
        await show_po(user_id=update.callback_query.from_user.id,
                      update=update,
                      page=int(cb_data[1]))
        return
    elif cb_data[0] == 'repeat':
        await repeat_order(order_num=int(cb_data[1]), update=update)
        return
    elif cb_data[0] == 'CB':
        await update.callback_query.edit_message_reply_markup(reply_markup=inline_menu_generation(cb_data[1]))
        return