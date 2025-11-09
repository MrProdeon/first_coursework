from utils.views_functions import operations_reader, create_datetime_object
import pandas as pd
from typing import Optional

def decorator_for_write_to_file(func):
    def wrapper(*args, **kwargs):
        pass
    return wrapper

df = operations_reader("../data/operations.xlsx")

def spending_by_category(transactions: pd.DataFrame,
                         category: str,
                         date: Optional[str] = None) -> pd.DataFrame:

    transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], dayfirst=True)

    if date is None:
        date = pd.Timestamp.today()
    else:
        date = pd.to_datetime(date)

    three_month_ago = date - pd.DateOffset(months=3)
    transactions_with_date = transactions[(transactions["Дата операции"] <= date)
    & (transactions["Дата операции"] >= three_month_ago)]

    transactions_with_category =  transactions_with_date[transactions_with_date["Категория"] == category]

    return transactions_with_category

print(spending_by_category(df, "Переводы", "2021-12-31 23:00:00"))





