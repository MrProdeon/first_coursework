import datetime
import json

from utils.views_functions import (create_datetime_object, get_currency_rate,
                                   get_expenses, get_incoming_operations,
                                   get_info_about_card, get_stocks_price,
                                   get_time_of_day_greeting,
                                   get_top_5_transactions, operations_reader)

path = r"..\data\operations.xlsx"


def main_page(date_string: str) -> str:

    date_object = create_datetime_object(date_string)
    date_start = date_object.replace(day=1, hour=0, minute=0, second=0)
    if date_object is None:
        raise ValueError(f"Невозможно преобразовать строку '{date_string}' в дату")
    greeting = get_time_of_day_greeting(date_object)

    operations = operations_reader(path).fillna("Информация не указана.")
    info_about_card = get_info_about_card(operations)
    top_5_transactions = get_top_5_transactions(operations)

    currency_rate = get_currency_rate()
    stocks_price = get_stocks_price()

    json_result = {
        "greeting": greeting,
        "cards": [card for card in info_about_card],
        "top_transactions": [transaction for transaction in top_5_transactions],
        "currency_rates": currency_rate,
        "stocks_prices": stocks_price,
    }

    return json.dumps(json_result, indent=4, ensure_ascii=False)


def events_page(date_string: str, date_range: str = "M") -> str:
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

    expenses = get_expenses(path, date_start, date_object)
    incoming = get_incoming_operations(path, date_start, date_object)
    currency_rate = get_currency_rate()
    stocks_price = get_stocks_price()

    json_result = {
        "expenses": expenses,
        "income": incoming,
        "currency_rates": currency_rate,
        "stocks_prices": stocks_price,
    }

    return json.dumps(json_result, indent=4, ensure_ascii=False)
