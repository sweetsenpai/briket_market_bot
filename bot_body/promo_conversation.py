from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler)

from briket_DB.promotions import chek_promo, sales_db, output_promotions
PROMO = range(1)


async def promo_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text='Введите промокод :')
    return PROMO


async def promo_end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    promo = update.message.text
    check_result = chek_promo(promo_code=promo, user_id=update.message.chat_id)
    if check_result[1] is False:
        await update.message.reply_text(text=check_result[0])
        return ConversationHandler.END

    await update.message.reply_text(text=check_result)
    return ConversationHandler.END


async def skip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return ConversationHandler.END


async def delete_promotion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard_buttons = []
    for pormotion in sales_db.find({"user_id": {"$exists": False}}):
        keyboard_buttons.append(
            [InlineKeyboardButton(text=output_promotions(pormotion), callback_data='del_promo,{}'.format(pormotion['code']))]
        )
    promo_keyboard = InlineKeyboardMarkup(keyboard_buttons)
    await update.message.reply_text('Выберете акцию которую хотите остановить из  списка ниже',
                                    reply_markup=promo_keyboard)
    return


