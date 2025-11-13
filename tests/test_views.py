from unittest.mock import patch, MagicMock
import json
import pytest

import utils.functions
from src.views import main_page


@patch("src.views.get_stocks_price", return_value=[{"AAPL": 10}])
@patch("src.views.get_currency_rate", return_value=[{"USD": 30}])
@patch("src.views.get_top_5_transactions", return_value=[{"Операция": "Покупка"}])
@patch("src.views.get_info_about_card", return_value=[{"Карта": "*4023"}])
@patch("src.views.create_datetime_object")
def test_main_page(mock_date, *_):
    from datetime import datetime
    # возвращаем реальный объект datetime, а не MagicMock
    mock_date.return_value = datetime(2025, 11, 11)

    result = main_page("2025-11-11 00:00:00")
    data = json.loads(result)

    assert "greeting" in data
    assert "cards" in data and data["cards"] == [{"Карта": "*4023"}]
    assert "top_transactions" in data and data["top_transactions"] == [{"Операция": "Покупка"}]
    assert "currency_rates" in data and data["currency_rates"] ==  [{"USD": 30}]
    assert "stocks_prices" in data and data["stocks_prices"] == [{"AAPL": 10}]