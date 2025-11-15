# mypy: ignore-errors

import json
from datetime import datetime
from unittest.mock import patch

import pandas as pd

from src.views import events_page, main_page


@patch("src.views.get_stocks_price", return_value=json.dumps([{"AAPL": 10}]))
@patch("src.views.get_currency_rate", return_value=json.dumps([{"USD": 30}]))
@patch("src.views.get_top_5_transactions", return_value=json.dumps([{"Операция": "Покупка"}]))
@patch("src.views.get_info_about_card", return_value=json.dumps([{"Карта": "*4023"}]))
@patch("src.views.create_datetime_object")
def test_main_page(mock_date, *_):
    mock_date.return_value = datetime(2025, 11, 11)

    result = main_page("2025-11-11 00:00:00")
    data = json.loads(result)

    assert "greeting" in data
    assert "cards" in data and data["cards"] == [{"Карта": "*4023"}]
    assert "top_transactions" in data and data["top_transactions"] == [{"Операция": "Покупка"}]
    assert "currency_rates" in data and data["currency_rates"] == [{"USD": 30}]
    assert "stocks_prices" in data and data["stocks_prices"] == [{"AAPL": 10}]


@patch("src.views.get_expenses", return_value=json.dumps([{"total_amount": 100}]))
@patch("src.views.get_incoming_operations", return_value=json.dumps([{"total_amount": 200}]))
@patch("src.views.get_currency_rate", return_value=json.dumps([{"USD": 30}]))
@patch("src.views.get_stocks_price", return_value=json.dumps([{"AAPL": 10}]))
@patch("src.views.create_datetime_object")
def test_events_page(mock_date, *_):
    mock_date.return_value = datetime(2025, 11, 11)
    df = pd.DataFrame()
    result = events_page(df, "2025-11-11", "M")

    data = json.loads(result)

    assert "expenses" in data
    assert "income" in data
    assert "currency_rates" in data
    assert "stocks_prices" in data

    assert data["expenses"] == [{"total_amount": 100}]
    assert data["income"] == [{"total_amount": 200}]
    assert data["currency_rates"] == [{"USD": 30}]
    assert data["stocks_prices"] == [{"AAPL": 10}]
