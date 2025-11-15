# mypy: ignore-errors
import json

import pandas as pd

from src.reports import (get_correct_dataframe, spending_by_category, spending_by_weekday, spending_by_workday,
                         write_to_file)


def test_write_to_file(get_df, tmp_path):
    file = tmp_path / "test_write_to_file.xlsx"

    @write_to_file(file)
    def rep(transactions: pd.DataFrame):
        return json.dumps(transactions.to_dict(orient="records"), ensure_ascii=False)

    result_df = rep(get_df)

    assert file.exists()

    df_from_file = pd.read_excel(file)

    pd.testing.assert_frame_equal(df_from_file, get_df, check_dtype=False)


def test_write_to_file_error(get_df):
    @write_to_file(123)
    def rep(transactions: pd.DataFrame):
        # Должна возвращать JSON строку, как все ваши функции
        return json.dumps(transactions.to_dict(orient="records"), ensure_ascii=False)

    result = rep(get_df)
    assert isinstance(result, pd.DataFrame)


def test_get_correct_dataframe(get_incoming):
    result = get_correct_dataframe(get_incoming, "2025-11-11 00:00:00")
    expected = [
        {
            "Дата операции": pd.Timestamp("2025-11-11 00:00:00"),
            "Сумма операции": -100,
            "Номер карты": "*4023",
            "Категория": "Фастфуд",
            "Описание": "Тест Фастфуд",
        },
        {
            "Дата операции": pd.Timestamp("2025-08-11 00:00:00"),
            "Сумма операции": -110,
            "Номер карты": "*4023",
            "Категория": "Переводы",
            "Описание": "Перевод Тест",
        },
    ]
    assert result.to_dict(orient="records") == expected

    none_result = get_correct_dataframe("no_dataframe", "2025-11-11 00:00:00")
    assert type(none_result) is pd.DataFrame


def test_spending_by_category(get_incoming):
    result = spending_by_category(get_incoming, "Фастфуд", "2025-11-11 00:00:00")
    assert result == json.dumps(
        [
            {
                "Дата операции": "2025-11-11 00:00:00",
                "Сумма операции": -100,
                "Номер карты": "*4023",
                "Категория": "Фастфуд",
                "Описание": "Тест Фастфуд",
            }
        ],
        ensure_ascii=False,
    )

    none_result = spending_by_category("eror", 123)
    assert none_result == json.dumps({})


def test_spending_by_weekday(get_another_df):
    result = spending_by_weekday(get_another_df, "2025-11-11 00:00:00")
    assert result == json.dumps(
        [
            {"День недели": "Понедельник", "Сумма операции": -110.0},
            {"День недели": "Вторник", "Сумма операции": -100.0},
        ],
        ensure_ascii=False,
    )

    none_result = spending_by_weekday(123, 123)
    assert none_result == json.dumps({}, ensure_ascii=False)


def test_spending_by_workday(get_another_df):
    result = spending_by_workday(get_another_df, "2025-11-11 00:00:00")
    assert result == json.dumps([{"Рабочий или выходной": "Рабочий", "Сумма операции": -105.0}], ensure_ascii=False)

    none_result = spending_by_workday(123, 123)
    assert none_result == json.dumps({}, ensure_ascii=False)
