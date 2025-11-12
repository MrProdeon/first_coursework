# mypy: ignore-errors

import datetime
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
import requests

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
    user_setting_reader,
)

path_to_file = "data/operations.xlsx"


def test_create_datetime_object():
    result = create_datetime_object("2025-11-10 00:00:00")
    date = datetime.datetime.strptime("2025-11-10 00:00:00", "%Y-%m-%d %H:%M:%S")
    assert result == date


@pytest.mark.parametrize(
    "data, expected", [("2025-aa-aa", None), ("2025-11_12", None), ("2025-11-10 00:00:123213", None)]
)
def test_failed_datetime_object(data, expected):
    result = create_datetime_object(data)
    assert result is expected


@pytest.mark.parametrize(
    "datetime_object, expected",
    [
        (datetime.datetime.strptime("2025-11-10 00:00:00", "%Y-%m-%d %H:%M:%S"), "Доброй ночи"),
        (datetime.datetime.strptime("2025-11-10 07:00:00", "%Y-%m-%d %H:%M:%S"), "Доброе утро"),
        (datetime.datetime.strptime("2025-11-10 13:00:00", "%Y-%m-%d %H:%M:%S"), "Добрый день"),
        (datetime.datetime.strptime("2025-11-10 18:00:00", "%Y-%m-%d %H:%M:%S"), "Добрый вечер"),
        ("error", None),
    ],
)
def test_get_time_of_dat_greeting(datetime_object, expected):
    assert get_time_of_day_greeting(datetime_object) == expected


def test_operations_reader():
    result = operations_reader(path_to_file)
    assert type(result) is pd.DataFrame


@patch("json.load")
def test_user_setting_reader(mock_load):
    mock_load.return_value = {"user_currencies": ["USD"], "user_stocks": ["AAPL"]}
    correct_result = user_setting_reader(path_to_file)
    assert correct_result == {"user_currencies": ["USD"], "user_stocks": ["AAPL"]}
    none_result = user_setting_reader("error_path")
    assert none_result is None


def test_get_info_about_card(get_df, get_date_object):
    result = get_info_about_card(get_df, get_date_object)
    assert result == [{"last_digits": "*4023", "total_spent": 100, "cashback": 1}]

    none_result = get_info_about_card("not_dataframe", get_date_object)
    assert none_result is None


def test_get_top_5_transactions(get_df, get_date_object):
    correct_result = get_top_5_transactions(get_df, get_date_object)
    assert correct_result == [
        {"date": pd.Timestamp("2025-11-11 00:00:00"), "amount": 100, "category": "Фастфуд", "description": "Тест"}
    ]

    none_result = get_top_5_transactions("not_dataframe", get_date_object)
    assert none_result is None


@patch("utils.functions.user_setting_reader", return_value={"user_currencies": ["USD", "EUR"]})
@patch("requests.get")
def test_get_currency_rate(mock_get, mock_user_setting):
    mock_get.return_value.json.return_value = {
        "Date": "2025-11-11T11:30:00+03:00",
        "PreviousDate": "2025-11-08T11:30:00+03:00",
        "PreviousURL": r"\/\/www.cbr-xml-daily.ru\/archive\/2025\/11\/08\/daily_json.js",
        "Timestamp": "2025-11-10T20:00:00+03:00",
        "Valute": {
            "USD": {
                "ID": "R01235",
                "NumCode": "840",
                "CharCode": "USD",
                "Nominal": 1,
                "Name": "Доллар США",
                "Value": 81.0132,
                "Previous": 81.2257,
            },
            "EUR": {
                "ID": "R01239",
                "NumCode": "978",
                "CharCode": "EUR",
                "Nominal": 1,
                "Name": "Евро",
                "Value": 93.9287,
                "Previous": 93.8365,
            },
        },
    }

    result = get_currency_rate()
    assert result == [{"currency": "USD", "rate": 81.0132}, {"currency": "EUR", "rate": 93.9287}]


@patch("requests.get")
def test_get_currency_rate_error(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError
    mock_get.return_value = mock_response

    result = get_currency_rate()
    assert result is None

    mock_response_2 = MagicMock()
    mock_response_2.status_code = 400
    mock_response_2.raise_for_status.side_effect = requests.exceptions.Timeout
    mock_get.return_value = mock_response_2

    result_2 = get_currency_rate()
    assert result_2 is None


@patch("utils.functions.user_setting_reader", return_value={"user_stocks": ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]})
@patch("requests.get")
def test_get_stocks_price(mock_get, mock_user_settings):
    def mock_response(url, headers):
        ticker = url.split("=")[-1]
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = {
            "ticker": ticker,
            "price": {"AAPL": 269.43, "AMZN": 248.4, "GOOGL": 290.1, "MSFT": 506, "TSLA": 445.23}[ticker],
        }
        return mock_resp

    mock_get.side_effect = mock_response

    result = get_stocks_price()

    assert result == [
        {"stock": "AAPL", "price": 269.43},
        {"stock": "AMZN", "price": 248.4},
        {"stock": "GOOGL", "price": 290.1},
        {"stock": "MSFT", "price": 506},
        {"stock": "TSLA", "price": 445.23},
    ]


df = pd.DataFrame(
    [
        {
            "Дата операции": ["11.11.2025 00:00:00", "2025-08-11 00:00:00"],
            "Сумма операции": [-100, 100],
            "Номер карты": ["*4023", "*4023"],
            "Категория": ["Фастфуд", "Переводы"],
            "Описание": ["Тест Фастфуд", "Перевод Тест"],
        }
    ]
)


def test_get_expenses(get_another_df, get_date_object, get_start_date_object):
    result = get_expenses(get_another_df, get_date_object, get_start_date_object)

    expected = {
        "total_amount": 210,
        "main": [{"category": "Переводы", "amount": 110}, {"category": "Фастфуд", "amount": 100}],
        "other": "-",
        "transfers_and_cash": [{"category": "Переводы", "amount": 110}],
    }

    assert result == expected

    none_result = get_expenses("test_error", get_date_object, get_start_date_object)
    assert none_result is None


def test_get_incoming_operations(get_incoming, get_date_object, get_start_date_object):
    result = get_incoming_operations(get_incoming, get_date_object, get_start_date_object)
    assert result == {"total_amount": 100, "main": [{"category": "Переводы", "amount": 100}]}

    result_with_no_start_date = get_incoming_operations(get_incoming, get_date_object)
    assert result_with_no_start_date == {"total_amount": 100, "main": [{"category": "Переводы", "amount": 100}]}

    none_result = get_incoming_operations("error", get_date_object, get_start_date_object)
    assert none_result is None
