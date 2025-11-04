import datetime
import json
import os

import pandas as pd
import requests
from dotenv import load_dotenv
from pandas.core.interchange.dataframe_protocol import DataFrame

load_dotenv()

APIKEY = os.getenv("APININJAS_KEY")

path = r"..\data\operations.xlsx"

user_setting_path = "../user_setting.json"

def create_datetime_object(date_str: str) -> datetime.datetime:
    """Функция для преобразования строковой даты в объект даты datetime"""
    date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")

    return date_obj


def get_time_of_day_greeting(date_object: datetime.datetime) -> str:
    """Функция для определения времени суток, использует часы в качестве определителя"""
    hour = date_object.hour

    if 5 <= hour <= 11:
        return "Доброе утро"
    elif 12 <= hour <= 17:
        return "Добрый день"
    elif 18 <= hour <= 22:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def operations_reader(path_to_file: str) -> pd.DataFrame:
    """Функция для чтения excel файла и создания датафрейма"""
    file = pd.read_excel(path_to_file)
    return file

def user_setting_reader(path_to_file : str) -> dict:
    with open(path_to_file, "r", encoding="UTF-8") as file:
        readed_file = json.load(file)

    return readed_file


def get_info_about_card(dataframe_with_operations: pd.DataFrame) -> list[dict]:
    """Функция для преобразования данных из датафрейма в информацию о номерах карт,
    общей сумме покупок по определенной карте и кэшбэка по определенной карте.
    Вернет список словарей, где каждый словарь - описанные выше данные
    """
    grouped_by_card = (
        dataframe_with_operations.groupby("Номер карты")
        .agg({"Сумма операции": "sum"})
        .abs()
    )
    grouped_by_card["Кэшбэк"] = grouped_by_card["Сумма операции"].abs() * 0.01
    grouped_by_card["Кэшбэк"] = grouped_by_card["Кэшбэк"].round(2)
    grouped_by_card.reset_index(inplace=True)
    grouped_by_card.rename(
        columns={
            "Номер карты": "last_digits",
            "Сумма операции": "total_spent",
            "Кэшбэк": "cashback",
        },
        inplace=True,
    )

    return grouped_by_card.to_dict(orient="records")


def get_top_5_transactions(dataframe_with_operations: pd.DataFrame) -> list:

    sorted_by_sum = dataframe_with_operations.sort_values(by="Сумма операции", ascending=False).head()
    sorted_by_sum.rename(
        columns={
            "Дата операции": "date",
            "Сумма операции": "amount",
            "Категория": "category",
            "Описание": "description",
        },
        inplace=True,
    )

    top_5_transaction_by_sum = []

    for index, row in sorted_by_sum.iterrows():
        searched_dict = {
            "date": row["date"],
            "amount": abs(row["amount"]),
            "category": row["category"],
            "description": row["description"],
        }
        top_5_transaction_by_sum.append(searched_dict)

    return top_5_transaction_by_sum


def get_currency_rate() -> list | None:
    url = "https://www.cbr-xml-daily.ru/daily_json.js"
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()

        dict_response = response.json()
        currency_rate = { currency : dict_response["Valute"][currency]["Value"]
        for currency in user_setting_reader(user_setting_path)["user_currencies"]
        }


        currency_rate_list = [{"currency": k, "rate": v} for k, v in currency_rate.items()]
        return currency_rate_list
    except requests.exceptions.HTTPError as error:
        print(f"Произошла ошибка : {error}")
        return None
    except requests.exceptions.Timeout:
        print("Время ожидания превысило ожидаемое.")
        return None


def get_stocks_price() -> list | None:
    headers = {"X-Api-Key": APIKEY}

    stocks_price_list: list[dict[str, float]] = []
    for ticker in user_setting_reader(user_setting_path).get("user_stocks", []):
        try:
            response_stock = requests.get(
                f"https://api.api-ninjas.com/v1/stockprice?ticker={ticker}", headers=headers
            )
            response_stock.raise_for_status()
            response_stock = response_stock.json()
            stocks_price_list.append({"stock" : response_stock["ticker"], "price" : response_stock["price"]})
        except requests.exceptions.HTTPError as error:
            print(f"Произошла ошибка {error}")
    return stocks_price_list