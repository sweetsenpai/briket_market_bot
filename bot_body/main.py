from briket_DB.passwords import test_bot_key, bot_key
from server.ngrok_tunel import get_https
from datetime import time
from payments.ykassa_integration import payment_finder
from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
    InlineQueryHandler,
    CallbackQueryHandler, AIORateLimiter)
from bot_body.user import registration as rg
import menu
from bot_body.shopping_cart import cart_show_button
from shopping_cart import call_back_handler
from bot_body.residents import resident_registration as res_reg
from bot_body.admin import admin_commands as ac, promo_conversation as promo, admin_registration as ar
from bot_body.admin.destribytion import start_distribution, get_text_destribution, cov_end, TEXT_DIST
from bot_body.admin.admin_promo import (add_promo_start, add_promo_onetime,
                                        add_promo_start_price,
                                        add_promo_procent, add_promo_text,
                                        add_promo_end, promo_distribution,
                                        cancel_command,
                                        CODE, TEXT, START_PRICE, ONE_TIME, PROCENT, START_DISTRIBUTION)
from functional_key import admin_keyboard, resident_keyboard, customer_keyboard, start, promo_keyboard
import briket_DB.reviews.review_conv as rv
import os
from delivery.yandex_api import driver_number_sender
from order_ofirm.pickup_conv import pickup_conversation
from order_ofirm.delivery_conv import del_conv
from user.addresses import show_addresses, add_conv
from briket_DB.shopping.cache_category import cache_category
from briket_DB.reports.user_data_report import user_data_updater
PORT = int(os.environ.get('PORT', '80'))


def main() -> None:
    application = Application.builder().token(bot_key).rate_limiter(AIORateLimiter()).build()

    reg_user = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('Регистрация'), rg.start)],
        states={
            rg.PHONE: [MessageHandler(filters.CONTACT, rg.phone)],
            rg.LOCATION: [MessageHandler(filters.LOCATION | filters.Regex('[а-яА-ЯёЁ]'), rg.location),
                          CommandHandler("skip", rg.skip_location), ],
            rg.INFO: [MessageHandler(filters.TEXT & ~filters.COMMAND, rg.info)],
            rg.EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, rg.email)]
        },
        fallbacks=[CommandHandler("cancel", rg.cancel)],
        conversation_timeout=600
    )

    reg_resident = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('Новый резидент вход'), res_reg.registration),
                      CommandHandler('registration', res_reg.registration)],
        states={
            res_reg.PHONE: [MessageHandler(filters.CONTACT, res_reg.phon_res)],
            res_reg.ADDRES: [MessageHandler(filters.LOCATION | filters.Regex('[а-яА-ЯёЁ]'), res_reg.resident_addres)],
            res_reg.NAME: [MessageHandler(filters.TEXT, res_reg.resident_name)],
            res_reg.EMAIL: [MessageHandler(filters.TEXT, res_reg.resident_email)],
            res_reg.DESCRIPTION: [MessageHandler(filters.TEXT, res_reg.resident_description)],
            res_reg.IMG: [MessageHandler(filters.PHOTO, res_reg.resident_img)]
        },
        fallbacks=[CommandHandler('cancel_reg', res_reg.resident_end)],
        conversation_timeout=600
    )
    reg_admin = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('Новый админ. вход'), ar.reg_admin_start),
                      CommandHandler('reg_admin_start', ar.reg_admin_start)],
        states={
            ar.PHONE: [MessageHandler(filters.CONTACT, ar.admin_email)],
            ar.EMAIL: [MessageHandler(filters.TEXT, ar.admin_final)]
        },
        fallbacks=[CommandHandler('admin_exit', ar.admin_exit)],
        conversation_timeout=600
    )

    ad_new_ad = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('Добавить админ.'), ac.add_new_admin_start)],
        states={
            ac.PHONE_AD_ADD: [MessageHandler(filters.TEXT, ac.add_new_admin_phone)]
        },
        fallbacks=[CommandHandler('stop', ac.cancel_conv)], conversation_timeout=600)

    del_admin = MessageHandler(filters.Regex('Удалить админ.'), ac.dele_admin)
    del_resident = MessageHandler(filters.Regex('Удалить резидента'), ac.del_resident)

    ad_new_resident = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('Добавить резидента'), ac.add_new_resident_start)],
        states={
            ac.PHONE_RS_ADD: [MessageHandler(filters.TEXT, ac.add_new_resident_end)],
        },
        fallbacks=[CommandHandler('stop', ac.cancel_conv)], conversation_timeout=600)

    promo_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('Активировать промокод'), promo.promo_start)],
        states={
            promo.PROMO: [MessageHandler(filters.TEXT, promo.promo_end)],
        },
        fallbacks=[CommandHandler('skip', promo.skip)], conversation_timeout=600)

    promo_creation = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('Создать промокод'), add_promo_start)],
        states={
            CODE: [MessageHandler(filters.TEXT, add_promo_text)],
            TEXT: [MessageHandler(filters.Regex('[а-яА-ЯёЁ]'), add_promo_onetime)],
            ONE_TIME: [MessageHandler(filters.TEXT, add_promo_start_price)],
            START_PRICE: [MessageHandler(filters.TEXT, add_promo_procent)],
            PROCENT: [MessageHandler(filters.TEXT, add_promo_end)],
            START_DISTRIBUTION: [MessageHandler(filters.TEXT, promo_distribution)]
        }, fallbacks=[CommandHandler('cancel', cancel_command)], conversation_timeout=600)

    dest_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('Создать рассылку'), get_text_destribution)],
        states={TEXT_DIST: [MessageHandler(filters.TEXT, start_distribution)]},
        fallbacks=[CommandHandler('cancel', cov_end)])

    user_rev_con = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('Оставить отзыв'), rv.start_rev)],
        states={
            rv.TEXT: [MessageHandler(filters.TEXT, rv.text_rev)],
            rv.LAST: [MessageHandler(filters.TEXT, rv.end_rev)]
        }, fallbacks=[CommandHandler('cancel', rv.cancel)], conversation_timeout=600)

    report = MessageHandler(filters.Regex('Отчет'), ac.report)
    ad_info = MessageHandler(filters.Regex('FAQ админ.'), ac.admin_info)
    res_info = MessageHandler(filters.Regex('FAQ рез.'), ac.resident_info)
    cust_info = MessageHandler(filters.Regex('FAQ'), rg.custommer_faq)
    application.add_handler(MessageHandler(filters.Regex('🛒Корзина🛒'), cart_show_button))
    application.add_handler(CommandHandler('admin_info', ac.admin_info))
    application.add_handler(MessageHandler(filters.Regex('Месячный'), ac.mouth_report))
    application.add_handler(MessageHandler(filters.Regex('За день'), ac.day_report))
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.Regex('Главное меню'), start))
    application.add_handler(user_rev_con)
    application.add_handler(MessageHandler(filters.Regex('Мои адреса'), show_addresses))
    application.add_handler(CommandHandler('instraction', ac.resident_info))
    application.add_handler(MessageHandler(filters.Regex('Аккаунт'), rg.custommer_account))
    application.add_handler(MessageHandler(filters.Regex('Промокоды'), promo_keyboard))
    application.add_handler(MessageHandler(filters.Regex('Активные промокоды'), promo.delete_promotion))
    application.add_handler(dest_conv)
    application.add_handler(promo_conv)
    application.add_handler(dest_conv)
    application.add_handler(report)
    application.job_queue.run_daily(callback=ac.day_report_job, time=time.fromisoformat('14:19:00+03:00'),
                                    job_kwargs={'misfire_grace_time': 60})
    application.job_queue.run_monthly(callback=ac.mouth_report_job,
                                      when=time.fromisoformat('12:00:00+03:00'),
                                      day=-1,
                                      job_kwargs={'misfire_grace_time': 60})
    application.job_queue.run_repeating(callback=driver_number_sender,
                                        interval=180,
                                        job_kwargs={'misfire_grace_time': 60})
    application.job_queue.run_repeating(callback=payment_finder,
                                        interval=30,
                                        job_kwargs={'misfire_grace_time': 15})
    application.job_queue.run_repeating(callback=cache_category,
                                        interval=600,
                                        job_kwargs={'misfire_grace_time': 15})
    application.job_queue.run_daily(callback=user_data_updater, time=time.fromisoformat('03:00:00+03:00'),
                                    job_kwargs={'misfire_grace_time': 60})
    application.add_handler(add_conv)
    application.add_handler(del_conv)
    application.add_handler(pickup_conversation)
    application.add_handler(ad_info)
    application.add_handler(res_info)
    application.add_handler(ad_new_ad)
    application.add_handler(del_resident)
    application.add_handler(ad_new_resident)
    application.add_handler(del_admin)
    application.add_handler(reg_admin)
    application.add_handler(reg_resident)
    application.add_handler(cust_info)
    application.add_handler(promo_creation)
    application.add_handler(CommandHandler('menu', menu.menu))
    application.add_handler(MessageHandler(filters.Regex('Меню'), menu.menu))
    application.add_handler(InlineQueryHandler(menu.inline_query))
    application.add_handler(reg_user)
    application.add_handler(CallbackQueryHandler(call_back_handler))
    application.add_handler(MessageHandler(filters.Regex('Администратор'), admin_keyboard))
    application.add_handler(MessageHandler(filters.Regex('Клиент'), customer_keyboard))
    application.add_handler(MessageHandler(filters.Regex('Резидент'), resident_keyboard))
#    application.run_polling()
    application.run_webhook(port=PORT, url_path=bot_key, webhook_url=f'{get_https()}/{bot_key}',
                        listen="0.0.0.0")


if __name__ == '__main__':
    main()
