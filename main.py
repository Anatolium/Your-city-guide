import telebot
from telebot import types
import requests
from datetime import datetime, timedelta
import re
from config import BOT_TOKEN

# Инициализация бота
bot = telebot.TeleBot(BOT_TOKEN)

# Конфигурация
KUDAGO_API_URL = "https://kudago.com/public-api/v1.4/events/"
cities = ["Москва", "Санкт-Петербург", "Нижний Новгород", "Екатеринбург", "Казань"]
city_slugs = {
    "Москва": "msk",
    "Санкт-Петербург": "spb",
    "Нижний Новгород": "nnov",
    "Екатеринбург": "ekb",
    "Казань": "kazan"
}
categories = {
    1: ["Концерты", "concert"],
    2: ["Спектакли", "theater"],
    6: ["Выставки", "exhibition"],
    7: ["Экскурсии", "tour"],
    8: ["Фестивали", "festival"],
    9: ["Кинопоказы", "cinema"],
    12: ["Праздники", "holiday"],
    36: ["Детям", "kids"],
    46: ["Активный отдых", "recreation"],
    47: ["Развлечения", "entertainment"]
}

user_data = {}

# Основное меню
def get_main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Смотреть события")
    markup.add("Выбрать город", "Выбрать категории", "Выбрать дату")
    return markup

# Функция для очистки HTML-тегов
def strip_html_tags(text):
    clean = re.compile('<.*?>')
    text = re.sub(clean, '', text)
    text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"').replace('&#39;', "'")
    text = ' '.join(text.split())
    return text

# Обработчик /start
@bot.message_handler(commands=['start'])
def start_handler(message):
    user_data[message.chat.id] = {"city": None, "categories": [], "date": None}
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for city in cities:
        markup.add(city)
    bot.send_message(message.chat.id, "Выберите город:", reply_markup=markup)

# Обработчик для кнопки "Выбрать город"
@bot.message_handler(func=lambda message: message.text == "Выбрать город")
def choose_city_handler(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for city in cities:
        markup.add(city)
    bot.send_message(message.chat.id, "Выберите город:", reply_markup=markup)

# Обработчик выбора города
@bot.message_handler(func=lambda message: message.text in cities)
def city_handler(message):
    user_data[message.chat.id]["city"] = message.text
    bot.send_message(message.chat.id, f"Вы выбрали {message.text}.", reply_markup=get_main_menu())
    bot.send_message(message.chat.id, "Теперь выберите категории событий:", reply_markup=get_categories_markup(message.chat.id))

# Выбор категорий
def get_categories_markup(chat_id):
    markup = types.InlineKeyboardMarkup()
    for key, value in categories.items():
        callback_data = f'cat_{key}'
        button_text = value[0]
        if key in user_data[chat_id]["categories"]:
            button_text += " ✅"
        markup.add(types.InlineKeyboardButton(button_text, callback_data=callback_data))
    markup.add(types.InlineKeyboardButton("Завершить выбор", callback_data="finish"))
    return markup

@bot.message_handler(func=lambda message: message.text == "Выбрать категории")
def categories_handler(message):
    bot.send_message(message.chat.id, "Выберите категории:", reply_markup=get_categories_markup(message.chat.id))

@bot.callback_query_handler(func=lambda call: call.data.startswith("cat_"))
def category_callback_handler(call):
    category_id = int(call.data.split("_")[1])
    if category_id in user_data[call.message.chat.id]["categories"]:
        user_data[call.message.chat.id]["categories"].remove(category_id)
    else:
        user_data[call.message.chat.id]["categories"].append(category_id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=get_categories_markup(call.message.chat.id))
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "finish")
def finish_callback_handler(call):
    selected_categories = [categories[i][0] for i in user_data[call.message.chat.id]["categories"]]
    if not selected_categories:
        bot.send_message(call.message.chat.id, "Вы не выбрали ни одной категории.", reply_markup=get_main_menu())
    else:
        bot.send_message(call.message.chat.id, "Вы выбрали категории:\n" + "\n".join(selected_categories), reply_markup=get_main_menu())
    bot.answer_callback_query(call.id)

# Выбор даты
@bot.message_handler(func=lambda message: message.text == "Выбрать дату")
def date_handler(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    today = datetime.now()
    for i in range(7):
        date = today + timedelta(days=i)
        markup.add(date.strftime("%d.%m.%Y"))
    markup.add("Отмена")
    bot.send_message(message.chat.id, "Выберите дату:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Отмена")
def cancel_date_handler(message):
    bot.send_message(message.chat.id, "Выбор даты отменен.", reply_markup=get_main_menu())

@bot.message_handler(regexp=r'^\d{2}\.\d{2}\.\d{4}$')
def save_date_handler(message):
    try:
        selected_date = datetime.strptime(message.text, "%d.%m.%Y")
        user_data[message.chat.id]["date"] = selected_date
        bot.send_message(message.chat.id, f"Вы выбрали дату: {message.text}.", reply_markup=get_main_menu())
    except ValueError:
        bot.send_message(message.chat.id, "Некорректный формат даты. Попробуйте снова.", reply_markup=get_main_menu())

# Функция для получения актуальных категорий
def fetch_categories():
    try:
        response = requests.get("https://kudago.com/public-api/v1.4/event-categories/", timeout=10)
        response.raise_for_status()
        categories_data = response.json()
        print(f"Доступные категории: {categories_data}")
        for cat in categories_data:
            print(f"ID: {cat['id']}, Название: {cat['name']}, Slug: {cat['slug']}")
        return categories_data
    except requests.RequestException as e:
        print(f"Ошибка при получении категорий: {e}")
        return None

# Просмотр событий
@bot.message_handler(func=lambda message: message.text == "Смотреть события")
def show_events_handler(message):
    chat_id = message.chat.id
    city = user_data.get(chat_id, {}).get("city")
    categories_list = user_data.get(chat_id, {}).get("categories", [])
    selected_date = user_data.get(chat_id, {}).get("date")

    if not city:
        bot.send_message(chat_id, "Сначала выберите город.", reply_markup=get_main_menu())
        return
    if not categories_list:
        bot.send_message(chat_id, "Сначала выберите категории.", reply_markup=get_main_menu())
        return
    if not selected_date:
        bot.send_message(chat_id, "Сначала выберите дату.", reply_markup=get_main_menu())
        return

    # Проверяем актуальные категории
    available_categories = fetch_categories()
    if available_categories:
        global categories
        new_categories = {}
        for cat in available_categories:
            new_categories[cat['id']] = [cat['name'], cat['slug']]
        if new_categories:
            categories = new_categories
            valid_categories = [cat for cat in categories_list if cat in categories]
            if not valid_categories:
                bot.send_message(chat_id, "Выбранные категории больше не поддерживаются. Пожалуйста, выберите категории заново.", reply_markup=get_main_menu())
                user_data[chat_id]["categories"] = []
                return
            categories_list = valid_categories

    # Сохраняем параметры для пагинации
    user_data[chat_id]["current_page"] = 1

    # Формирование списка slug'ов категорий
    category_slugs = [categories[cat_id][1] for cat_id in categories_list]

    # Формирование запроса к KudaGo API
    params = {
        'location': city_slugs[city],
        'categories': ','.join(category_slugs),
        'actual_since': int(selected_date.timestamp()),
        'actual_until': int((selected_date + timedelta(days=1)).timestamp()),
        'fields': 'id,title,description,price,place,site_url',
        'page_size': 5,
        'page': user_data[chat_id]["current_page"]
    }

    try:
        print(f"Отправляем запрос с параметрами: {params}")
        response = requests.get(KUDAGO_API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        events = data.get('results', [])
        user_data[chat_id]["has_next_page"] = data.get('next') is not None

        if not events:
            bot.send_message(
                chat_id,
                "События для выбранных категорий не найдены. Попробуйте выбрать другие категории или дату.",
                reply_markup=get_main_menu()
            )
            return

        for event in events:
            title = event.get('title', 'Без названия')
            description = strip_html_tags(event.get('description', 'Нет описания'))
            description = description[:200] + '...' if len(description) > 200 else description
            price = event.get('price', 'Цена не указана')
            place = event.get('place', {})
            place_name = place.get('title', 'Место не указано') if isinstance(place, dict) else 'Место не указано'
            site_url = event.get('site_url', '')
            message_text = (
                f"🎭 *{title}*\n"
                f"📍 *Место:* {place_name}\n"
                f"💰 *Цена:* {price}\n"
                f"📜 *Описание:* {description}\n"
            )
            if site_url:
                message_text += f"🔗 [Подробнее]({site_url})"
            bot.send_message(chat_id, message_text, parse_mode='Markdown', disable_web_page_preview=True)

        # Добавляем кнопки пагинации
        markup = get_main_menu()
        if user_data[chat_id]["has_next_page"]:
            markup.add("Следующая страница")
        bot.send_message(chat_id, "Поиск завершен.", reply_markup=markup)

    except requests.RequestException as e:
        bot.send_message(chat_id, f"Ошибка при получении событий: {str(e)}", reply_markup=get_main_menu())
        print(f"Полный ответ сервера: {e.response.text if e.response else 'Нет ответа'}")

# Обработчик для следующей страницы
@bot.message_handler(func=lambda message: message.text == "Следующая страница")
def next_page_handler(message):
    chat_id = message.chat.id
    city = user_data.get(chat_id, {}).get("city")
    categories_list = user_data.get(chat_id, {}).get("categories", [])
    selected_date = user_data.get(chat_id, {}).get("date")

    if not all([city, categories_list, selected_date]):
        bot.send_message(chat_id, "Данные устарели. Начните поиск заново.", reply_markup=get_main_menu())
        return

    # Увеличиваем номер страницы
    user_data[chat_id]["current_page"] += 1

    # Формирование списка slug'ов категорий
    category_slugs = [categories[cat_id][1] for cat_id in categories_list]

    # Формирование запроса к KudaGo API
    params = {
        'location': city_slugs[city],
        'categories': ','.join(category_slugs),
        'actual_since': int(selected_date.timestamp()),
        'actual_until': int((selected_date + timedelta(days=1)).timestamp()),
        'fields': 'id,title,description,price,place,site_url',
        'page_size': 6,
        'page': user_data[chat_id]["current_page"]
    }

    try:
        print(f"Отправляем запрос с параметрами (страница {user_data[chat_id]['current_page']}): {params}")
        response = requests.get(KUDAGO_API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        events = data.get('results', [])
        user_data[chat_id]["has_next_page"] = data.get('next') is not None

        if not events:
            bot.send_message(chat_id, "Больше событий нет.", reply_markup=get_main_menu())
            return

        for event in events:
            title = event.get('title', 'Без названия')
            description = strip_html_tags(event.get('description', 'Нет описания'))
            description = description[:200] + '...' if len(description) > 200 else description
            price = event.get('price', 'Цена не указана')
            place = event.get('place', {})
            place_name = place.get('title', 'Место не указано') if isinstance(place, dict) else 'Место не указано'
            site_url = event.get('site_url', '')
            message_text = (
                f"🎭 *{title}*\n"
                f"📍 *Место:* {place_name}\n"
                f"💰 *Цена:* {price}\n"
                f"📜 *Описание:* {description}\n"
            )
            if site_url:
                message_text += f"🔗 [Подробнее]({site_url})"
            bot.send_message(chat_id, message_text, parse_mode='Markdown', disable_web_page_preview=True)

        # Обновляем кнопки пагинации
        markup = get_main_menu()
        if user_data[chat_id]["has_next_page"]:
            markup.add("Следующая страница")
        bot.send_message(chat_id, f"Страница {user_data[chat_id]['current_page']}.", reply_markup=markup)

    except requests.RequestException as e:
        bot.send_message(chat_id, f"Ошибка при получении событий: {str(e)}", reply_markup=get_main_menu())
        print(f"Полный ответ сервера: {e.response.text if e.response else 'Нет ответа'}")

# Запуск бота
if __name__ == '__main__':
    try:
        print("Бот запущен...")
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Ошибка при запуске бота: {e}")