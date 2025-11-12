import logging
import os
from functools import wraps
from typing import Callable, Optional

import pandas as pd

from utils.functions import operations_reader

logs_path = os.path.join(os.path.dirname(__file__), "..", "logs", "reports.log")
logger = logging.getLogger(__name__)
if not logger.handlers:
    file_handler = logging.FileHandler(logs_path, encoding="UTF-8", mode="a")
    file_formatter = logging.Formatter("%(asctime)s %(message)s %(funcName)s %(filename)s %(lineno)s")
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    logger.setLevel(logging.DEBUG)


def write_to_file(filename: str = "report.xlsx") -> Callable:
    """Декоратор для записи отчета в файл. По умолчанию запись идет в report.xlsx,
    но можно указать нужное название файла"""
    logger.info(f"Начало работы декоратора, запись в файл {filename}")

    def get_report(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: pd.DataFrame | Optional[str], **kwargs: pd.DataFrame | Optional[str]) -> pd.DataFrame:
            try:
                df: pd.DataFrame = func(*args, **kwargs)
                df.to_excel(filename, index=False)
                logger.info("Произошла успешная запись в файл")
                return df
            except Exception as error:
                logger.error(f"Во время записи произошла ошибка {error}")
                return df

        return wrapper

    return get_report


df = operations_reader("data/operations.xlsx")


def get_correct_dataframe(transactions: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    """
    Функция для фильтрации датафрейма.
    :param transactions: Датафрейм, нуждающийся в фильтрации
    :param date: Дата, до которой будет получен датафрейм. Получение идет за три месяца до этой даты.
    :return: Отфильтрованный датафрейм с нужной датой и только с расходами
    """
    try:
        logger.info("Начало работы функции")
        transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], dayfirst=True)

        if date is None:
            date_obj = pd.Timestamp.today()
        else:
            date_obj = pd.to_datetime(date)

        three_month_ago = date_obj - pd.DateOffset(months=3)
        transactions_with_date = transactions[
            (transactions["Дата операции"] <= date_obj) & (transactions["Дата операции"] >= three_month_ago)
        ]

        only_expenses = transactions_with_date[transactions_with_date["Сумма операции"] < 0]

        return only_expenses
    except Exception as error:
        logger.error(f"Произошла ошибка {error}")
        return pd.DataFrame()


def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """
    Функция для фильтрации датафрейма по указанной категории и дате за три месяца.
    :param transactions: Датафрейм для фильтрации
    :param category: Категория для поиска
    :param date: Дата, до которой будет произведен поиск.
    Анализируются транзакции за последние три месяца до этой даты.
    :return: отфильтрованный датафрейм
    """
    try:
        logger.info("Начало работы функции")
        only_expenses = get_correct_dataframe(transactions, date)

        transactions_with_category = only_expenses[only_expenses["Категория"] == category]
        logger.info("Успешное завершение функции")
        return transactions_with_category
    except Exception as error:
        logger.error(f"Произошла ошибка {error}")
        return pd.DataFrame()


def spending_by_weekday(transactions: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    """
    Функция для поиска среднеарефмитических трат по дням недели за последние три месяца
    до указанной даты. Если дата не указана - от сегодняшнего дня.
    :param transactions: Датафрейм для фильтрации
    :param date: Дата, до которой будет произведен поиск.
    Анализируются транзакции за последние три месяца до этой даты.
    :return: датафрейм с днями недели и средних трат за эти дни в течение 3 месяцев.
    """
    try:
        logger.info("Начало работы функции")
        only_expenses = get_correct_dataframe(transactions, date)

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

        only_expenses["День недели"] = only_expenses["День недели"].map(days)

        avg_amount_per_day = only_expenses.groupby(by="День недели", as_index=False).agg({"Сумма операции": "mean"})

        weekday_order = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
        avg_amount_per_day["Порядок"] = avg_amount_per_day["День недели"].apply(lambda x: weekday_order.index(x))
        avg_amount_per_day = avg_amount_per_day.sort_values(by="Порядок").drop(columns="Порядок")
        logger.info("Функция успешно завершила работу")
        return avg_amount_per_day
    except Exception as error:
        logger.error(f"Произошла ошибка {error}")
        return pd.DataFrame()


def spending_by_workday(transactions: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    """
    Функция для анализа среднеарефмитических трат по выходным и будним дням за последние три месяца
    до указанной даты
    :param transactions: Датафрейм для фильтрации
    :param date: Дата, до которой будет произведен поиск.
    Анализируются транзакции за последние три месяца до этой даты.
    :return: датафрейм с информацией о средних тратах по выходным и будням за последние 3 месяца до
    указанной даты. Если дата не указана - за последние 3 месяца от сегодняшнего дня.
    """
    try:
        logger.info("Начало работы функции")
        only_expenses = get_correct_dataframe(transactions, date)

        only_expenses["День недели"] = only_expenses["Дата операции"].dt.weekday

        def work_or_weekend(day: int) -> str:
            if day <= 4:
                return "Рабочий"
            else:
                return "Выходной"

        only_expenses["Рабочий или выходной"] = only_expenses["День недели"].apply(work_or_weekend)

        expenses_by_workday = only_expenses.groupby(by="Рабочий или выходной", as_index=False).agg(
            {"Сумма операции": "mean"}
        )
        logger.info("Функция успешно завершила свою работу")
        return expenses_by_workday
    except Exception as error:
        logger.error(f"Произошла ошибка {error}")
        return pd.DataFrame()
