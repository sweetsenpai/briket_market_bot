from telegram import (ReplyKeyboardMarkup,
                      KeyboardButton,
                      Update,
                      InlineKeyboardMarkup,
                      InlineKeyboardButton)
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters, CommandHandler
from briket_DB.sql_main_files.customers import addres_keyboard, insert_new_addres

ONE = range(1)


async def show_addresses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text='Для того, чтобы удалить один аз адресов, просто нажмите на него.',
                                        reply_markup=(inline_addresses(update.message.from_user.id)))
    await update.message.reply_text(text='Для того, чтобы добавить новый адрес, нажмите на клавиатуру.',
                                        reply_markup=ReplyKeyboardMarkup([[KeyboardButton('Добавить новый адрес')]]))

    return


def inline_addresses(user_id):
    keyboard = []
    for address in addres_keyboard(user_id):
        keyboard.append([
            InlineKeyboardButton(text=address, callback_data=f'remove_address,{address}')
        ])
    return InlineKeyboardMarkup(keyboard)


async def address_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text='Введите адрес.')
    return ONE


async def address_end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    address = update.message.text
    insert_new_addres(chat_id=update.message.from_user.id,
                      addres=address)
    await update.message.reply_text(text='Адрес успешно добавлен.')
    await show_addresses(update, context)
    return ConversationHandler.END


def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return ConversationHandler.END


add_conv = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex('Добавить новый адрес'), address_start)],
    states={
        ONE: [MessageHandler(filters.TEXT, address_end)]
    },
    fallbacks=[CommandHandler('stop', stop)])