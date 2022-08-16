from briket_DB.passwords import bot_key
from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters)
import registration as rg


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

    application.add_handler(reg_user)
    application.run_polling()


if __name__ == '__main__':
    main()