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

    transactions["Дата платежа"] = pd.to_datetime(transactions["Дата платежа"], dayfirst=True)

    if date is None:
        date = pd.Timestamp.today()
    else:
        date = pd.to_datetime(date)

    three_month_ago = date - pd.DateOffset(months=3)
    transactions_with_date = transactions[(transactions["Дата платежа"] <= date)
    & (transactions["Дата платежа"] >= three_month_ago)]

    only_expenses = transactions_with_date[transactions_with_date["Сумма операции"] < 0]

    transactions_with_category =  only_expenses[only_expenses["Категория"] == category]

    return transactions_with_category


def spending_by_weekday(transactions: pd.DataFrame,
                        date: Optional[str] = None) -> pd.DataFrame:
    transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], dayfirst=True)

    if date is None:
        date = pd.Timestamp.today()
    else:
        date = pd.to_datetime(date)

    three_month_ago = date - pd.DateOffset(months=3)
    transactions_with_date = transactions[(transactions["Дата операции"] <= date)
                                          & (transactions["Дата операции"] >= three_month_ago)]

    only_expenses = transactions_with_date[transactions_with_date["Сумма операции"] < 0].copy()

    only_expenses["День недели"] = only_expenses["Дата операции"].dt.weekday

    days = {
        0: "Понедельник",
        1: "Вторник",
        2: "Среда",
        3: "Четверг",
        4: "Пятница",
        5: "Суббота",
        6: "Воскресенье",
    }

    only_expenses["День недели"]= only_expenses["День недели"].map(days)

    avg_amount_per_day = (only_expenses.groupby(by="День недели", as_index=False).agg({"Сумма операции":"mean"}))


    weekday_order = ["Понедельник","Вторник","Среда","Четверг","Пятница","Суббота","Воскресенье"]
    avg_amount_per_day["Порядок"] = avg_amount_per_day["День недели"].apply(lambda x: weekday_order.index(x))
    avg_amount_per_day = avg_amount_per_day.sort_values(by="Порядок").drop(columns="Порядок")

    return avg_amount_per_day

def spending_by_workday(transactions: pd.DataFrame,
                        date: Optional[str] = None) -> pd.DataFrame:
    transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], dayfirst=True)

    if date is None:
        date = pd.Timestamp.today()
    else:
        date = pd.to_datetime(date)

    three_month_ago = date - pd.DateOffset(months=3)
    transactions_with_date = transactions[(transactions["Дата операции"] <= date)
                                          & (transactions["Дата операции"] >= three_month_ago)]

    only_expenses = transactions_with_date[transactions_with_date["Сумма операции"] < 0].copy()

    only_expenses["День недели"] = only_expenses["Дата операции"].dt.weekday

    def work_or_weekend(day):
        if day <= 4:
            return "Рабочий"
        else:
            return "Выходной"

    only_expenses["Рабочий или выходной"] = only_expenses["День недели"].apply(work_or_weekend)

    expenses_by_workday = only_expenses.groupby(by="Рабочий или выходной", as_index=False).agg({"Сумма операции" : "mean"})

    return expenses_by_workday

#print(spending_by_workday(df, "2019-10-01 00:00:00"))








