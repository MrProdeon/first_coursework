import json
import logging
import os
import re
from math import ceil
from typing import Any

import pandas as pd

path_to_file = "data/operations.xlsx"
logs_path = os.path.join(os.path.dirname(__file__), "..", "logs", "services.log")
logger = logging.getLogger(__name__)
if not logger.handlers:
    file_handler = logging.FileHandler(logs_path, encoding="UTF-8", mode="a")
    file_formatter = logging.Formatter("%(asctime)s %(message)s %(funcName)s %(filename)s %(lineno)s")
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    logger.setLevel(logging.DEBUG)


def profitable_cashback(readed_file: pd.DataFrame, year: str, month: str) -> str:
    """Функция для анализа выгоды, полученной от кэшбэка.
    Принимает путь до файла с операциями, год для анализа и месяц для анализа.
    Возвращает JSON, состоящий из словаря, в котором отображены все кэшбэки
    по категориям на выбранный год и месяц"""
    resulted_dict = {}
    try:
        logger.info("Начало работы функции")

        readed_file["Дата операции"] = pd.to_datetime(readed_file["Дата операции"], dayfirst=True)

        filter_file = readed_file[
            (readed_file["Дата операции"].dt.year == int(year)) & (readed_file["Дата операции"].dt.month == int(month))
        ]

        grouped_by_category = (
            filter_file.groupby(by="Категория", as_index=False)
            .agg({"Кэшбэк": "sum"})
            .sort_values(by="Кэшбэк", ascending=False)
        )

        resulted_dict = {
            row["Категория"]: row["Кэшбэк"] for index, row in grouped_by_category.iterrows() if row["Кэшбэк"] > 0
        }
    except Exception as error:
        logger.error(f"Произошла ошибка {error}")
        return json.dumps(resulted_dict)
    return json.dumps(resulted_dict, indent=4, ensure_ascii=False)


def investment_bank(month: str, transactions: list[dict[str, Any]], limit: int) -> float | str:
    """
    Функция для анализа информации о том, сколько можно было накопить, используя инвесткопилку
    :param month: Месяц, за который хотим получить информацию.
    ВАЖНО : Передается с формате год-месяц -> "2020-01"
    :param transactions: список словарей с информацией о транзакциях
    :param limit: сумма округления
    :return: сумма, которую удалось бы накопить, используя данное окгругление. Либо Строку ошибки, если
    не удалось выполнить функцию.
    """
    try:
        logger.info("Начало работы функции")
        year, month = month.split("-")

        df = pd.DataFrame(transactions)
        df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True)
        df = df[
            (df["Дата операции"].dt.year == int(year))
            & (df["Дата операции"].dt.month == int(month))
            & (df["Сумма операции"] < 0)
        ]

        result: float = round(
            sum(
                [
                    (ceil(abs(row["Сумма операции"]) / limit) * limit) - abs(row["Сумма операции"])
                    for index, row in df.iterrows()
                ]
            ),
            2,
        )
        return result

    except Exception as error:
        logger.error(f"Произошла ошибка {error}")
        return "Произошла ошибка во время выполнения"


def simple_search(transactions: list[dict[str, Any]], string_for_search: str) -> str:
    """Функция для поиска подстроки в описании или категории. Принимает список словарей
    из транзакций и строку для поиска.
    Возвращает JSON, в котором все списки словарей, у которых в описании или категории
    имеется передаваемая строка"""
    result = []
    try:
        logger.info("Начало работы функции")
        pattern = re.compile(rf"{string_for_search}")
        result = [
            dict_ for dict_ in transactions if pattern.search(dict_["Описание"]) or pattern.search(dict_["Категория"])
        ]
    except Exception as error:
        logger.error(f"Произошла ошибка {error}")
        return json.dumps(result)

    return json.dumps(result, indent=4, ensure_ascii=False)


def phone_number_search(transactions: list[dict[str, Any]]) -> str:
    """Функция для поиска транзакций, у которых в описании указан номер телефона.
    Принимает список словарей из транзакций.
    Возвращает JSON, в котором все списки словарей, у которых в описании есть номер телефона.
    """
    result = []
    try:
        logger.info("Начало работы функции")
        pattern = re.compile(r"\+\d+\s+\d+\s+\d+-\d+-\d+")
        result = [dict_ for dict_ in transactions if pattern.search(dict_["Описание"])]
    except Exception as error:
        logger.error(f"Произошла ошибка {error}")
        return json.dumps(result)

    return json.dumps(result, indent=4, ensure_ascii=False)


def remittance_search(transactions: list[dict[str, Any]]) -> str:
    """Функция для поиска переводов физическим лицам.
    Принимает список словарей из операций.
    Возвращает JSON, в котором список словарей, состоящий из тех словарей, в котором категория -
    это переводы, а в описании указано имя получателя и первая буква его фамилии с точкой."""
    result = []
    try:
        logger.info("Начало работы функции")
        pattern = re.compile(r"[А-ЯЁ][а-яё]+\s+[А-ЯЁ]\.$")
        result = [
            dict_
            for dict_ in transactions
            if pattern.search(dict_["Описание"]) and re.search("Переводы", dict_["Категория"])
        ]
    except Exception as error:
        logger.error(f"Произошла ошибка {error}")
        return json.dumps(result)

    return json.dumps(result, indent=4, ensure_ascii=False)
