import datetime
import json

import pandas as pd

from utils.functions import (
    create_datetime_object,
    get_currency_rate,
    get_expenses,
    get_incoming_operations,
    get_info_about_card,
    get_stocks_price,
    get_time_of_day_greeting,
    get_top_5_transactions,
    operations_reader,
)

path = r"data\operations.xlsx"
df = operations_reader(path)
readed_file = df if df is not None and not df.empty else pd.DataFrame()


def main_page(date_string: str) -> str:
    """Функция для формирования JSON-объекта, который будет использован для отображения
    главной страницы банковского приложения.

    На вход принимает строку с датой, после чего преобразует в datetime.
    Исходя из того какое время суток, формирует ответ для пользователя: "Доброе утро",
    "Добрый день", "Добрый вечер", "Доброй ночи"

    В функции происходит чтение excel файла и формируется информация о всех картах, а так же
    о пяти самых больших транзакциях. Формирование происходит только за текущий месяц, с начала месяца
    до дня, указанного в принимаемой дате.

    Дополнительно происходит формирование курса валют и цен на акции. Какие валюты и акции искать, указано
    в файле user_setting.json
    """

    date_object = create_datetime_object(date_string)
    if date_object is None:
        raise ValueError(f"Невозможно преобразовать строку '{date_string}' в дату")
    greeting = get_time_of_day_greeting(date_object)

    operations = readed_file
    operations = operations.fillna("Информация не указана.")
    info_about_card = get_info_about_card(operations, date_object) or []
    top_5_transactions = get_top_5_transactions(operations, date_object) or []

    currency_rate: list[dict[str, int | float]] | None = get_currency_rate() or []
    stocks_price: list[dict[str, int | float]] | None = get_stocks_price() or []

    json_result = {
        "greeting": greeting,
        "cards": [card for card in info_about_card],
        "top_transactions": [transaction for transaction in top_5_transactions],
        "currency_rates": currency_rate,
        "stocks_prices": stocks_price,
    }

    return json.dumps(json_result, indent=4, ensure_ascii=False, default=str)


def events_page(operations : pd.DataFrame,date_string: str, date_range: str = "M") -> str:
    """Функция для формирования JSON-объекта, который будет использоваться для отображения
    страницы 'События' в приложении банка.
    Принимает на вход строку даты и диапазон для поиска.

    Формирует информация о расходах, такую как общая сумма расходов, раздел "основные", в котором траты по
    категориям отсортированы по убыванию. Указаны 7 категорий с наибольшими тратами, а всё что не вошло -
    суммируется и добавляется в раздел "Другое".
    Формирует раздел "Перевод и наличные", которую сортирует по убыванию.

    Формирует раздел поступлений, в котором есть общая сумма поступлений и раздел "Основные", в котором
    поступления по категориям отсортированы по убыванию.

    Дополнительно происходит формирование курса валют и цен на акции. Какие валюты и акции искать, указано
    в файле user_setting.json
    """
    date_object = create_datetime_object(date_string)
    if date_object is None:
        raise ValueError(f"Невозможно преобразовать строку '{date_string}' в дату")
    if date_range == "W":
        date_start = date_object - datetime.timedelta(days=date_object.weekday())
    elif date_range == "M":
        date_start = date_object.replace(day=1, hour=0, minute=0, second=0)
    elif date_range == "Y":
        date_start = date_object.replace(month=1, day=1, hour=0, minute=0, second=0)
    elif date_range == "ALL":
        date_start = None

    expenses = get_expenses(operations, date_start, date_object)
    incoming = get_incoming_operations(operations, date_start, date_object)
    currency_rate = get_currency_rate()
    stocks_price = get_stocks_price()

    json_result = {
        "expenses": expenses,
        "income": incoming,
        "currency_rates": currency_rate,
        "stocks_prices": stocks_price,
    }

    return json.dumps(json_result, indent=4, ensure_ascii=False)
