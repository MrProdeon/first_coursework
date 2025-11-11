from utils.functions import operations_reader, create_datetime_object
import pytest
import pandas as pd


path_to_file = "../data/operations.xlsx"

@pytest.fixture
def get_df():
    df = pd.DataFrame([
        {"Дата операции" : "11.11.2025 00:00:00",
         "Сумма операции" : -100,
         "Номер карты" : "*4023",
         "Категория" : "Фастфуд",
         "Описание" : "Тест"
         }
    ])
    return df

@pytest.fixture
def get_date_object():
    result = create_datetime_object("2025-11-11 20:00:00")
    return result

@pytest.fixture
def get_start_date_object():
    result = create_datetime_object("2025-08-11 00:00:00")
    return result

@pytest.fixture
def get_another_df():
    df = pd.DataFrame([
        {"Дата операции": "11.11.2025 00:00:00",
         "Сумма операции": -100,  # int
         "Номер карты": "*4023",
         "Категория": "Фастфуд",
         "Описание": "Тест Фастфуд"},
        {"Дата операции": "2025-08-11 00:00:00",
         "Сумма операции": -100,  # int
         "Номер карты": "*4023",
         "Категория": "Переводы",
         "Описание": "Перевод Тест"},
    ])
    return df