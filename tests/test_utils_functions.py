import pandas as pd
import pytest
import datetime

from utils.functions import create_datetime_object, get_time_of_day_greeting, operations_reader

def test_create_datetime_object():
    result = create_datetime_object("2025-11-10 00:00:00")
    date = datetime.datetime.strptime("2025-11-10 00:00:00", "%Y-%m-%d %H:%M:%S")
    assert result == date


@pytest.mark.parametrize("data, expected", [
    ("2025-aa-aa", None),
    ("2025-11_12", None),
    ("2025-11-10 00:00:123213", None)
])
def test_failed_datetime_object(data, expected):
    result = create_datetime_object(data)
    assert result is expected


@pytest.mark.parametrize("datetime_object, expected", [
    (datetime.datetime.strptime("2025-11-10 00:00:00", "%Y-%m-%d %H:%M:%S"), "Доброй ночи"),
    (datetime.datetime.strptime("2025-11-10 07:00:00", "%Y-%m-%d %H:%M:%S"), "Доброе утро"),
    (datetime.datetime.strptime("2025-11-10 13:00:00", "%Y-%m-%d %H:%M:%S"), "Добрый день"),
    (datetime.datetime.strptime("2025-11-10 18:00:00", "%Y-%m-%d %H:%M:%S"), "Добрый вечер"),
    ('error', None)
])
def test_get_time_of_dat_greeting(datetime_object, expected):
    assert get_time_of_day_greeting(datetime_object) == expected

def test_operations_reader():
    result = operations_reader("../data/operations.xlsx")
    assert type(result) == pd.DataFrame
    assert operations_reader('here.xlsx') == None


