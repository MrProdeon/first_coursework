import json

from utils.main_page_functions import (create_datetime_object,
                                       get_currency_rate, get_info_about_card,
                                       get_stocks_price,
                                       get_time_of_day_greeting,
                                       get_top_5_transactions,
                                       operations_reader)


def main_page(date_sting: str) -> str:

    date_object = create_datetime_object(date_sting)
    greeting = get_time_of_day_greeting(date_object)

    operations = operations_reader(r"../data/operations.xlsx").fillna(
        "Информация не указана."
    )
    info_about_card = get_info_about_card(operations)
    top_5_transactions = get_top_5_transactions(operations)

    currency_rate = get_currency_rate()
    stocks_price = get_stocks_price()

    json_result = {
        "greeting": greeting,
        "cards": [card for card in info_about_card],
        "top_transactions": [transaction for transaction in top_5_transactions],
        "currency_rates": currency_rate,
        "stocks_prices": stocks_price,
    }

    return json.dumps(json_result, indent=4, ensure_ascii=False)
