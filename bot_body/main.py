from briket_DB.passwords import bot_key
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
from briket_DB.db_builder import *


def main() -> None:
    application = Application.builder().token(bot_key).build()
    reg_user = ConversationHandler(
        entry_points=[CommandHandler("start", rg.start)],
        states={
            rg.PHONE: [MessageHandler(filters.CONTACT, rg.phone)],
            rg.LOCATION: [MessageHandler(filters.LOCATION, rg.location),
                          CommandHandler("skip", rg.skip_location), ],
            rg.INFO: [MessageHandler(filters.TEXT & ~filters.COMMAND, rg.info)]
        },
        fallbacks=[CommandHandler("cancel", rg.cancel)],

    )

    reg_resident = ConversationHandler(
        entry_points=[CommandHandler('registration', res_reg.registration)],
        states={
            res_reg.PHONE: [MessageHandler(filters.CONTACT, res_reg.phon_res)],
            res_reg.ADDRES: [MessageHandler(filters.LOCATION, res_reg.resident_addres)],
            res_reg.NAME: [MessageHandler(filters.TEXT, res_reg.resident_name)],
            res_reg.EMAIL: [MessageHandler(filters.TEXT, res_reg.resident_email)],
            res_reg.DESCRIPTION: [MessageHandler(filters.TEXT, res_reg.resident_description)],
            res_reg.IMG: [MessageHandler(filters.PHOTO, res_reg.resident_img)]
        },
        fallbacks=[CommandHandler('cancel_reg', res_reg.resident_end)]
    )
    application.add_handler(reg_resident)
    application.add_handler(CommandHandler('menu', menu.menu))
    application.add_handler(InlineQueryHandler(menu.inline_query))
    application.add_handler(reg_user)
    application.add_handler(CallbackQueryHandler(call_back_handler))
    application.run_polling()


if __name__ == '__main__':
    main()
