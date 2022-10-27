from briket_DB.passwords import test_bot_key, bot_key
from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
    InlineQueryHandler,
    CallbackQueryHandler)
import registration as rg
import menu
from shopping_cart import call_back_handler
import resident_registration as res_reg
import admin_registration as ar
import admin_commands as ac
from functional_key import admin_keyboard, resident_keyboard, customer_keyboard, start
import os
from briket_DB.db_builder import *
PORT = int(os.environ.get('PORT', '8443'))


def main() -> None:
    application = Application.builder().token(bot_key).build()

    reg_user = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('Регистрация'), rg.start)],
        states={
            rg.PHONE: [MessageHandler(filters.CONTACT, rg.phone)],
            rg.LOCATION: [MessageHandler(filters.LOCATION | filters.TEXT, rg.location),
                          CommandHandler("skip", rg.skip_location), ],
            rg.INFO: [MessageHandler(filters.TEXT & ~filters.COMMAND, rg.info)]
        },
        fallbacks=[CommandHandler("cancel", rg.cancel)],

    )

    reg_resident = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('Новый резидент вход'), res_reg.registration)],
        states={
            res_reg.PHONE: [MessageHandler(filters.CONTACT, res_reg.phon_res)],
            res_reg.ADDRES: [MessageHandler(filters.LOCATION | filters.TEXT, res_reg.resident_addres)],
            res_reg.NAME: [MessageHandler(filters.TEXT, res_reg.resident_name)],
            res_reg.EMAIL: [MessageHandler(filters.TEXT, res_reg.resident_email)],
            res_reg.DESCRIPTION: [MessageHandler(filters.TEXT, res_reg.resident_description)],
            res_reg.IMG: [MessageHandler(filters.PHOTO, res_reg.resident_img)]
        },
        fallbacks=[CommandHandler('cancel_reg', res_reg.resident_end)]
    )

    reg_admin = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('Новый админ. вход'), ar.reg_admin_start)],
        states={
            ar.PHONE: [MessageHandler(filters.CONTACT, ar.admin_email)],
            ar.EMAIL: [MessageHandler(filters.TEXT, ar.admin_final)]
        },
        fallbacks=[CommandHandler('admin_exit', ar.admin_exit)]
    )

    ad_new_ad = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('Добавить админ.'), ac.add_new_admin_start)],
        states={
            ac.PHONE_AD_ADD: [MessageHandler(filters.TEXT, ac.add_new_admin_phone)]
        },
        fallbacks=[CommandHandler('stop', ac.cancel_conv)])

    del_admin = MessageHandler(filters.Regex('Удалить админ.'), ac.dele_admin)
    del_resident = MessageHandler(filters.Regex('Удалить резидента'), ac.del_resident)

    ad_new_resident = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('Добавить резидента'), ac.add_new_resident_start)],
        states={
            ac.PHONE_RS_ADD: [MessageHandler(filters.TEXT, ac.add_new_resident_end)],
        },
        fallbacks=[CommandHandler('stop', ac.cancel_conv)])

    report = MessageHandler(filters.Regex('Отчет'), ac.report)
    ad_info = MessageHandler(filters.Regex('FAQ админ.'), ac.admin_info)
    res_info = MessageHandler(filters.Regex('FAQ рез.'), ac.resident_info)
    cust_info = MessageHandler(filters.Regex('FAQ'), rg.custommer_faq)
    application.add_handler(CommandHandler('admin_info', ac.admin_info))
    application.add_handler(CommandHandler('start', start))
    application.add_handler(report)
    application.add_handler(ad_info)
    application.add_handler(res_info)
    application.add_handler(ad_new_ad)
    application.add_handler(del_resident)
    application.add_handler(ad_new_resident)
    application.add_handler(del_admin)
    application.add_handler(reg_admin)
    application.add_handler(reg_resident)
    application.add_handler(cust_info)
    application.add_handler(CommandHandler('menu', menu.menu))
    application.add_handler(MessageHandler(filters.Regex('Меню'), menu.menu))
    application.add_handler(InlineQueryHandler(menu.inline_query))
    application.add_handler(reg_user)
    application.add_handler(CallbackQueryHandler(call_back_handler))
    application.add_handler(MessageHandler(filters.Regex('Администратор'), admin_keyboard))
    application.add_handler(MessageHandler(filters.Regex('Клиент'), customer_keyboard))
    application.add_handler(MessageHandler(filters.Regex('Резидент'), resident_keyboard))
#    application.run_polling()
    application.run_webhook(port=PORT, url_path=bot_key, webhook_url=f'https://brikettestbot.herokuapp.com/{bot_key}',
                           listen="0.0.0.0")


if __name__ == '__main__':
    main()

