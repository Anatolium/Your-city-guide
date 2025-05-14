import sqlite3
import os
from actions import *

# Упрощение для данного бота (берём 10 видов событий вместо 21 на kudago):
event_categories_dict = {
    1: ["concert", "Концерты"],
    2: ["theater", "Спектакли"],
    6: ["exhibition", "Выставки"],
    7: ["tour", "Экскурсии"],
    8: ["festival", "Фестивали"],
    9: ["cinema", "Кинопоказы"],
    12: ["holiday", "Праздники"],
    36: ["kids", "Детям"],
    46: ["recreation", "Активный отдых"],
    47: ["entertainment", "Развлечения"]
}


def fill_table_cities(cursor):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            name TEXT NOT NULL,
            city_id INTEGER,
            city_slug TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            user_id INTEGER,
            category_id INTEGER,
            category_slug TEXT
        )
    ''')

    # Запрос к системной таблице sqlite_master, которая содержит метаинформацию о всех объектах БД
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cities';")
    if cursor.fetchone() is None:
        # Создание таблицы, если она не существует
        cursor.execute('''
            CREATE TABLE cities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                slug TEXT NOT NULL,
                name TEXT NOT NULL
            );
        ''')
        need_data_fill = True
    else:
        # Проверка, содержит ли таблица записи
        cursor.execute("SELECT COUNT(*) FROM cities;")
        if cursor.fetchone()[0] == 0:
            need_data_fill = True
        else:
            need_data_fill = False

    if need_data_fill:
        # Получение данных о городах и добавление их в таблицу
        cities_data = get_cities()
        #print(cities_data)
        for city in cities_data:
            cursor.execute("INSERT INTO cities (slug, name) VALUES (?, ?);", (city['slug'], city['name']))


def fill_table_event_categories(cursor):
    # Запрос к системной таблице sqlite_master, которая содержит метаинформацию о всех объектах БД
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='event_categories';")
    if cursor.fetchone() is None:
        # Создание таблицы, если она не существует
        cursor.execute('''
            CREATE TABLE event_categories (
                id INTEGER PRIMARY KEY,
                slug TEXT NOT NULL,
                name TEXT NOT NULL
            );
        ''')
        need_data_fill = True
    else:
        # Проверка, содержит ли таблица записи
        cursor.execute("SELECT COUNT(*) FROM event_categories;")
        if cursor.fetchone()[0] == 0:
            need_data_fill = True
        else:
            need_data_fill = False

    if need_data_fill:
        for key, value in event_categories_dict.items():
            cursor.execute("INSERT INTO event_categories (id, slug, name) VALUES (?,?,?)",
                           (key, value[0], value[1]))


def init_db():
    # Создание директории, если она не существует
    os.makedirs('data', exist_ok=True)

    # Подключение к базе данных
    conn = sqlite3.connect('data/city_guide.db')
    cursor = conn.cursor()

    fill_table_cities(cursor)
    fill_table_event_categories(cursor)

    # Сохранение изменений и закрытие соединения с базой данных
    conn.commit()
    conn.close()
