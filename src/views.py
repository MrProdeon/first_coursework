import datetime
import pandas as pd
from pandas.core.interchange.dataframe_protocol import DataFrame
import requests
from requests import RequestException, HTTPError

path = r"..\data\operations.xlsx"

def create_datetime_object(date_str : str) -> datetime.datetime:
    """Функция для преобразования строковой даты в объект даты datetime"""
    date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")

    return date_obj

def get_time_of_day(date_object : datetime.datetime) -> str:
    """Функция для определения времени суток, использует часы в качестве определителя"""
    hour = date_object.hour

    if 5 <= hour <= 11:
        return "Утро"
    elif 12 <= hour <= 17:
        return "День"
    elif 18 <= hour <= 22:
        return "Вечер"
    else:
        return "Ночь"


def operations_reader(path_to_file : str) -> DataFrame:
    """Функция для чтения excel файла и создания датафрейма"""
    file = pd.read_excel(path_to_file)
    return file

def get_info_about_card(dataframe_with_operations : DataFrame) -> dict:
    """Функция для преобразования данных из датафрейма в информацию о номерах карт,
    общей сумме покупок по определенной карте и кэшбэка по определенной карте.
    Вернет список словарей, где каждый словарь - описанные выше данные
    """
    grouped_by_card = dataframe_with_operations.groupby("Номер карты").agg({"Сумма операции" : "sum"}).abs()
    grouped_by_card["Кэшбэк"] = round(grouped_by_card["Сумма операции"]) * 0.01
    grouped_by_card.reset_index(inplace=True)
    grouped_by_card.rename(columns={"Номер карты" : "last_digits",
                                    "Сумма операции" : "total_spent",
                                    "Кэшбэк" : "cashback"}, inplace=True)

    return grouped_by_card.to_dict(orient="records")

def get_top_5_transactions(dataframe_with_operations : DataFrame) -> dict:

    sorted_by_sum = dataframe_with_operations.sort_values(by="Сумма операции").head()
    sorted_by_sum.rename(columns={
        "Дата операции" : "date",
        "Сумма операции" : "amount",
        "Категория" : "category",
        "Описание" : "description"

    }, inplace=True)

    top_5_transaction_by_sum = []

    for index, row in sorted_by_sum.iterrows():
        searched_dict = {
            "date" : row["date"],
            "amount" : abs(row["amount"]),
            "category" : row["category"],
            "description" : row["description"]
        }
        top_5_transaction_by_sum.append(searched_dict)

    return top_5_transaction_by_sum

def get_currency_rate():
    url = "https://www.cbr-xml-daily.ru/daily_json.js"
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()

        dict_response = response.json()
        currency_rate = {
            "USD" : dict_response["Valute"]["USD"]["Value"],
            "EUR" : dict_response["Valute"]["EUR"]["Value"]
        }
        return currency_rate
    except requests.exceptions.HTTPError as error:
        print(f"Произошла ошибка : {error}")
        return None
    except requests.exceptions.Timeout as error:
        print(f"Время ожидания превысило ожидаемое.")
        return None

print(get_currency_rate())





