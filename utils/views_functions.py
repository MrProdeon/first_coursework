import datetime
import json
import logging
import os

import pandas as pd
import requests
from dotenv import load_dotenv
from collections import Counter

logger = logging.getLogger(__name__)
file_handler = logging.FileHandler("../logs/main_page.log", encoding="UTF-8", mode="a")
file_formatter = logging.Formatter(
    "%(asctime)s %(message)s %(funcName)s %(filename)s %(lineno)s"
)
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)

load_dotenv()

APIKEY = os.getenv("APININJAS_KEY")

path = r"..\data\operations.xlsx"

user_setting_path = "../user_setting.json"


def create_datetime_object(date_str: str) -> datetime.datetime | None:
    """Функция для преобразования строковой даты в объект даты datetime"""
    logger.info("Начало работы функции create_datetime_object")
    try:
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        logger.info(
            "Конец работы функции create_datetime_object, успешное форматирование даты"
        )
        return date_obj
    except Exception as error:
        logger.error(f"В функции create_datetime_object произошла ошибка {error}")
        return None


def get_time_of_day_greeting(date_object: datetime.datetime) -> str | None:
    """Функция для определения времени суток, использует часы в качестве определителя"""
    logger.info("Начало работы функции get_time_of_day_greeting")
    hour = date_object.hour
    try:
        if 5 <= hour <= 11:
            logger.info("Функция get_time_of_day_greeting определила, что сейчас утро")
            return "Доброе утро"
        elif 12 <= hour <= 17:
            logger.info("Функция get_time_of_day_greeting определила, что сейчас день")
            return "Добрый день"
        elif 18 <= hour <= 22:
            logger.info("Функция get_time_of_day_greeting определила, что сейчас вечер")
            return "Добрый вечер"
        else:
            logger.info("Функция get_time_of_day_greeting определила, что сейчас ночь")
            return "Доброй ночи"
    except Exception as error:
        logger.error(f"В функции get_time_of_day_greeting произошла ошибка {error}")
        return None


def operations_reader(path_to_file: str) -> pd.DataFrame:
    """Функция для чтения excel файла и создания датафрейма"""
    try:
        logger.info(f"Начало чтения файла {path_to_file}")
        file = pd.read_excel(path_to_file)
    except Exception as error:
        logger.error(f"В функции operations_reader произошла ошибка {error}")
    return file


def user_setting_reader(path_to_file: str) -> dict:
    """Функция для чтения пользовательских настроек из json-файла, в котором есть список словарей"""
    logger.info(f"Начало чтения файла {path_to_file}")
    try:
        with open(path_to_file, "r", encoding="UTF-8") as file:
            logger.info("Файл успешно открыт")
            readed_file = json.load(file)
            logger.info("Файл успешно загружен в пайтон-объект")
    except Exception as error:
        logger.error(f"В функции user_setting_reader произошла ошибка {error}")

    return readed_file


def get_info_about_card(dataframe_with_operations: pd.DataFrame) -> list[dict]:
    """Функция для преобразования данных из датафрейма в информацию о номерах карт,
    общей сумме покупок по определенной карте и кэшбэка по определенной карте.
    Вернет список словарей, где каждый словарь - описанные выше данные
    """
    try:

        dataframe_with_operations = dataframe_with_operations[
            dataframe_with_operations["Сумма операции"] < 0
        ]
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
    except Exception as error:
        logger.error(f"В функции get_info_about_card произошла ошибка {error}")

    return grouped_by_card.to_dict(orient="records")


def get_top_5_transactions(dataframe_with_operations: pd.DataFrame) -> list:
    try:
        dataframe_with_operations = dataframe_with_operations[
            dataframe_with_operations["Сумма операции"] < 0
        ]
        sorted_by_sum = dataframe_with_operations.sort_values(
            by="Сумма операции", ascending=True
        ).head()
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
    except Exception as error:
        logger.error(f"В функции get_top_5_transactions произошла ошибка {error}")

    return top_5_transaction_by_sum


def get_currency_rate() -> list | None:
    url = "https://www.cbr-xml-daily.ru/daily_json.js"
    try:
        logger.info("Начало работы функции")
        response = requests.get(url, timeout=15)
        response.raise_for_status()

        dict_response = response.json()
        currency_rate = {
            currency: dict_response["Valute"][currency]["Value"]
            for currency in user_setting_reader(user_setting_path)["user_currencies"]
        }

        currency_rate_list = [
            {"currency": k, "rate": v} for k, v in currency_rate.items()
        ]
        return currency_rate_list
    except requests.exceptions.HTTPError as error:
        logger.error(f"Произошла ошибка {error}")
        print(f"Произошла ошибка : {error}")
        return None
    except requests.exceptions.Timeout as error:
        print("Время ожидания превысило ожидаемое.")
        logger.error(f"Произошла ошибка {error}")
        return None


def get_stocks_price() -> list | None:
    headers = {"X-Api-Key": APIKEY}
    try:
        stocks_price_list: list[dict[str, float]] = []
        for ticker in user_setting_reader(user_setting_path).get("user_stocks", []):
            try:
                response_stock = requests.get(
                    f"https://api.api-ninjas.com/v1/stockprice?ticker={ticker}",
                    headers=headers,
                )
                response_stock.raise_for_status()
                response_stock = response_stock.json()
                stocks_price_list.append(
                    {
                        "stock": response_stock["ticker"],
                        "price": response_stock["price"],
                    }
                )
            except requests.exceptions.HTTPError as error:
                print(f"Произошла ошибка {error}")
    except Exception as error:
        logger.error(f"Произошла ошибка {error}")
    return stocks_price_list


##############


def get_expenses(path_to_file: str, date_range : str) -> dict:
    operations = operations_reader(path_to_file)

    expenses = operations[operations["Сумма операции"] < 0].copy()
    expenses["abs_sum"] = expenses["Сумма операции"].abs()

    total_expenses = expenses["abs_sum"].sum() # Общая сумма расходов.


    grouped_by_categories = (
        expenses.groupby(by="Категория", as_index=False)
        .agg({"abs_sum": "sum"})
        .sort_values(by="abs_sum", ascending=False)
    )
    main_expenses_in_categories = [
        {"category": row["Категория"], "amount": int(row["abs_sum"])}
        for index, row in grouped_by_categories.head(7).iterrows()
    ] # Раздел «Основные»

    other_expenses = [
        int(row["abs_sum"])
        for index, row in grouped_by_categories.iloc[7:].iterrows()
    ]

    transfers_and_cash = (
        expenses.loc[expenses["Категория"].isin(["Переводы", "Наличные"])]
        .groupby("Категория", as_index=False)["abs_sum"]
        .sum()
    ).sort_values(by="abs_sum", ascending=False)
    transfers_and_cash_list = [
        {"category": row["Категория"], "amount": int(row["abs_sum"])}
        for index, row in transfers_and_cash.iterrows()
    ] # Раздел «Переводы и наличные»

    expenses_dict = {
        "total_amount" : int(total_expenses),
        "main" : main_expenses_in_categories,
        "other": sum(other_expenses) if len(other_expenses) > 0 else "-",
        "transfers_and_cash" : transfers_and_cash_list,
    }
    return expenses_dict

def get_incoming_operations(path_to_file: str) -> dict:
    operations = operations_reader(path_to_file)

    incoming = operations[operations["Сумма операции"] > 0]

    total_incoming = incoming["Сумма операции"].sum()

    main_incoming = (incoming.groupby("Категория", as_index=False).
                     agg({"Сумма операции" : "sum"}).
                     sort_values(by="Сумма операции",
                     ascending=False))

    main_incoming = [{row["Категория"]: int(row["Сумма операции"])} for index, row in main_incoming.iterrows()]

    incoming_dict = {
        "total_amount" : total_incoming,
        "main" : main_incoming
    }

    return incoming_dict
