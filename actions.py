import requests


def get_cities() -> list:
    url = "https://kudago.com/public-api/v1.4/locations/"
    params = {
        'lang': 'ru',
        'fields': 'slug,name'
    }
    response = requests.get(url, params=params)
    response.raise_for_status()  # Проверка на ошибки HTTP-запроса

    return response.json()


def get_event_categories() -> list:
    url = "https://kudago.com/public-api/v1.4/event-categories/"
    params = {
        'lang': 'ru',
        'order_by': 'id',
        'fields': 'id,name'
    }
    response = requests.get(url, params=params)
    response.raise_for_status()  # Проверка на ошибки HTTP-запроса

    return response.json()
