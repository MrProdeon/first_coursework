import pandas as pd
import json
from utils.views_functions import operations_reader
import datetime
from math import ceil
import re

from typing import Any

path = r"..\data\operations.xlsx"

# def profitable_cashback(path_to_data_file : str, year : str, month : str) -> str:
#     """Функция для анализа выгоды, полученной от кэшбэка.
#     Принимает путь до файла с операциями, год для анализа и месяц для анализа.
#     Возвращает JSON, состоящий из словаря, в котором отображены все кэшбэки
#     по категориям на выбранный год и месяц"""
#
#     readed_file = operations_reader(path_to_data_file)
#
#     readed_file["Дата операции"] = pd.to_datetime(readed_file["Дата операции"], dayfirst=True)
#
#     filter_file = readed_file[(readed_file["Дата операции"].dt.year == int(year))
#     & (readed_file["Дата операции"].dt.month == int(month))]
#
#     grouped_by_category = (filter_file.groupby(by="Категория", as_index=False)
#                            .agg({"Кэшбэк": "sum"})
#                            .sort_values(by="Кэшбэк", ascending=False))
#
#     resulted_dict = {row["Категория"] : row["Кэшбэк"]
#                      for index, row in grouped_by_category.iterrows()
#                      if row["Кэшбэк"] > 0}
#
#     return json.dumps(resulted_dict,indent=4, ensure_ascii=False)
#
#
df = operations_reader(path).fillna("Информация не указана.")
transactions = df.to_dict(orient="records")

# df = df[["Дата операции", "Сумма операции"]]
# transactions = [{"Дата операции" : row["Дата операции"],
#                  "Сумма операции" : row["Сумма операции"]} for index,row in df.iterrows()]
#
# def investment_bank(month: str, transactions: list[dict[str, Any]], limit: int) -> float:
#     year, month = month.split("-")
#
#     df = pd.DataFrame(transactions)
#     df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True)
#     df = df[(df["Дата операции"].dt.year == int(year)) & (df["Дата операции"].dt.month == int(month))
#     & (df["Сумма операции"] < 0)]
#
#     result = round(sum([(ceil(abs(row["Сумма операции"]) / limit) * limit) - abs(row["Сумма операции"])
#               for index, row in df.iterrows()]), 2)
#
#
#     return result

def simple_search(transactions : list[dict[str,Any]], string_for_search : str) -> str:
    """Функция для поиска подстроки в описании или категории. Принимает список словарей
    из транзакций и строку для поиска.
    Возвращает JSON, в котором все списки словарей, у которых в описании или категории
    имеется передаваемая строка"""
    pattern = re.compile(rf"{string_for_search}")
    result = [dict_ for dict_ in transactions
              if pattern.search(dict_["Описание"])
              or pattern.search(dict_["Категория"])]

    return json.dumps(result, indent=4, ensure_ascii=False)

def phone_number_search(transactions : list[dict[str,Any]]) -> str:
    """Функция для поиска транзакций, у которых в описании указан номер телефона.
    Принимает список словарей из транзакций.
    Возвращает JSON, в котором все списки словарей, у которых в описании есть номер телефона.
    """
    pattern = re.compile(r"\+\d+ \d+ \d+-\d+-\d+")
    result = [dict_ for dict_ in transactions
              if pattern.search(dict_["Описание"])]

    return json.dumps(result, indent=4, ensure_ascii=False)

def remittance_search(transactions : list[dict[str,Any]]) -> str:
    """Функция для поиска переводов физическим лицам.
    Принимает список словарей из операций.
    Возвращает JSON, в котором список словарей, состоящий из тех словарей, в котором категория -
    это переводы, а в описании указано имя получателя и первая буква его фамилии с точкой."""
    pattern = re.compile(r"^[А-Я][а-я]+ [А-Я]\.$")
    result = [dict_ for dict_ in transactions
              if pattern.search(dict_["Описание"])
              and re.search("Переводы", dict_["Категория"])
              ]

    return json.dumps(result, indent=4, ensure_ascii=False)
