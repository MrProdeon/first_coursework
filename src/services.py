import pandas as pd
import json
from utils.views_functions import operations_reader
import datetime

path = r"..\data\operations.xlsx"

def profitable_cashback(path_to_data_file : str, year : str, month : str) -> str:
    """Функция для анализа выгоды, полученной от кэшбэка.
    Принимает путь до файла с операциями, год для анализа и месяц для анализа.
    Возвращает JSON, состоящий из словаря, в котором отображены все кэшбэки
    по категориям на выбранный год и месяц"""

    readed_file = operations_reader(path_to_data_file)

    readed_file["Дата операции"] = pd.to_datetime(readed_file["Дата операции"], dayfirst=True)

    filter_file = readed_file[(readed_file["Дата операции"].dt.year == int(year))
    & (readed_file["Дата операции"].dt.month == int(month))]

    grouped_by_category = (filter_file.groupby(by="Категория", as_index=False)
                           .agg({"Кэшбэк": "sum"})
                           .sort_values(by="Кэшбэк", ascending=False))

    resulted_dict = {row["Категория"] : row["Кэшбэк"]
                     for index, row in grouped_by_category.iterrows()
                     if row["Кэшбэк"] > 0}

    return json.dumps(resulted_dict,indent=4, ensure_ascii=False)
