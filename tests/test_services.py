# mypy: ignore-errors

import json

from src.services import investment_bank, phone_number_search, profitable_cashback, remittance_search, simple_search


def test_profitable_cashback(get_another_df):
    result = profitable_cashback(get_another_df, "2025", "11")
    assert result == '{\n    "Фастфуд": 100\n}'

    empty_result = profitable_cashback("not_df", "2025", "11")
    assert empty_result == "{}"


def test_investment_bank(data_for_investment_bank):
    result = investment_bank("2025-11", data_for_investment_bank, 100)
    assert result == 130


def test_investment_bank_error(data_for_investment_bank):
    error_result = investment_bank("2025-11", "no_data", 100)

    assert error_result == "Произошла ошибка во время выполнения"


def test_simple_search(get_list_of_dicts):
    result = simple_search(get_list_of_dicts, "Переводы")
    assert json.loads(result) == [
        {
            "Дата операции": "11.08.2025 00:00:00",
            "Сумма операции": -110,
            "Номер карты": "*4023",
            "Категория": "Переводы",
            "Описание": "Артём Н.",
        },
        {
            "Дата операции": "11.11.2025 00:00:00",
            "Сумма операции": 100,
            "Номер карты": "*4023",
            "Категория": "Переводы",
            "Описание": "+7 937 701-21-08",
        },
    ]

    empty_result = simple_search("error", "error")
    assert empty_result == "[]"


def test_phone_number_search(get_list_of_dicts):
    result = phone_number_search(get_list_of_dicts)
    assert json.loads(result) == [
        {
            "Дата операции": "11.11.2025 00:00:00",
            "Сумма операции": 100,
            "Номер карты": "*4023",
            "Категория": "Переводы",
            "Описание": "+7 937 701-21-08",
        }
    ]

    empty_result = phone_number_search("no_data")
    assert empty_result == "[]"


def test_remittance_search(get_list_of_dicts):
    result = remittance_search(get_list_of_dicts)
    assert json.loads(result) == [
        {
            "Дата операции": "11.08.2025 00:00:00",
            "Сумма операции": -110,
            "Номер карты": "*4023",
            "Категория": "Переводы",
            "Описание": "Артём Н.",
        }
    ]

    empty_result = remittance_search(123)
    assert empty_result == "[]"
