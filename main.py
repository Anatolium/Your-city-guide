# @Your_city_guide_bot
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
import sqlite3
from init_db import *


# Настройка логирования
# logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
#
# def start(update: Update, context: CallbackContext):
#     keyboard = []
#     conn = sqlite3.connect('data/city_guide.db')
#     cursor = conn.cursor()
#     cursor.execute("SELECT name FROM cities")
#     cities = cursor.fetchall()
#     for city in cities:
#         city_name = city[0]
#         keyboard.append([InlineKeyboardButton(city_name, callback_data=f"city_{city_name}")])
#     reply_markup = InlineKeyboardMarkup(keyboard)
#     update.message.reply_text('Выберите город:', reply_markup=reply_markup)
#     cursor.close()
#     conn.close()
#
# def city_callback(update: Update, context: CallbackContext):
#     query = update.callback_query
#     query.answer()
#     city = query.data.split('_')[1]
#     keyboard = []
#     conn = sqlite3.connect('data/city_guide.db')
#     cursor = conn.cursor()
#     cursor.execute("SELECT id, name FROM event_categories")
#     event_categories = cursor.fetchall()
#     for event_category in event_categories:
#         event_id, event_name = event_category
#         keyboard.append([InlineKeyboardButton(event_name, callback_data=f"event_{event_id}")])
#     keyboard.append([InlineKeyboardButton("Назад", callback_data="back_to_city")])
#     reply_markup = InlineKeyboardMarkup(keyboard)
#     query.edit_message_text(text=f"Выбран город: {city}. Теперь выберите вид события:", reply_markup=reply_markup)
#     cursor.close()
#     conn.close()
#
# def event_callback(update: Update, context: CallbackContext):
#     query = update.callback_query
#     query.answer()
#     data = query.data
#     if data == "back_to_city":
#         start(update, context)
#     else:
#         event_id = data.split('_')[1]
#         print(f"get_events({event_id})")
#         query.edit_message_text(text=f"Вызвана функция get_events({event_id})")
#
# def main():
#     # Создаем Updater и передаем ему токен вашего бота.
#     # updater = Updater("YOUR_TELEGRAM_BOT_TOKEN", use_context=True)
#     updater = Updater("7143393444:AAFiQ9wDTEB9K9D7DT-80vpLR5-ChMuGk0g", use_context=True)
#
#     # Получаем диспетчер для регистрации обработчиков
#     dispatcher = updater.dispatcher
#
#     # Регистрация команды /start
#     dispatcher.add_handler(CommandHandler("start", start))
#
#     # Регистрация обработчика для кнопок
#     dispatcher.add_handler(CallbackQueryHandler(city_callback, pattern='^city_'))
#     dispatcher.add_handler(CallbackQueryHandler(event_callback, pattern='^event_|^back_to_city'))
#
#     # Запуск бота
#     updater.start_polling()
#     updater.idle()

if __name__ == '__main__':
    # Вызов функции для инициализации базы данных
    try:
        init_db()
    except Exception as e:
        print(f"Error: {e}")
    else:
        print("OK")

    #main()
