import datetime
import json
from typing import Any, cast

import pandas as pd

from src.reports import spending_by_category, spending_by_weekday, spending_by_workday, write_to_file
from src.services import investment_bank, phone_number_search, profitable_cashback, remittance_search, simple_search
from src.views import events_page, show_main_page
from utils.functions import operations_reader

NOW_TIME = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
TIME_FOR_TEST = "2019-11-11 00:00:00"
path = r"data\operations.xlsx"
df = operations_reader(path)
if df is None:
    df = pd.DataFrame()
df_list_of_dicts = cast(list[dict[str, Any]], df.to_dict(orient="records"))
readed_file = df if df is not None and not df.empty else pd.DataFrame()


def main() -> None:
    # main_page start
    show_main_page(TIME_FOR_TEST)

    # menu start
    while True:
        selected_section = input(
            """Для перехода в раздел, выберите номер, соответствующий разделу: 
1 -  «Главная»
2 -  «События»
3 -  «Отчёты»
4 -  «Сервисы»
5 -  Выйти из приложения
---> 
"""
        )
        while selected_section not in ("1", "2", "3", "4", "5"):
            selected_section = input("Ваш выбор: ")
        if selected_section == "1":
            show_main_page(TIME_FOR_TEST)
        elif selected_section == "2":
            print("Раздел «События»")
            events = json.loads(events_page(readed_file, TIME_FOR_TEST, "ALL"))
            print("Расходы: ")
            print("-" * 40)
            print("Общая сумма расходов: ")
            print(events["expenses"]["total_amount"])
            print("-" * 40)
            print("Основные расходы: ")
            for expense in events["expenses"]["main"]:
                print(f'Категория: {expense["category"]}')
                print(f'Сумма: {expense["amount"]}')
            print("-" * 40)
            print("Остальное: ")
            print(events["expenses"]["other"])
            print("-" * 40)
            print("Переводы и наличные: ")
            for operation in events["expenses"]["transfers_and_cash"]:
                print(f"Категория: {operation["category"]}")
                print(f"Сумма: {operation["amount"]}")
            print("=" * 40)
            print("Курс выбранных валют:")
            for rate in events["currency_rates"]:
                print(f"Валюта: {rate["currency"]}")
                print(f"стоимость: {rate["rate"]}")
                print("-" * 40)
            print("=" * 40)
            print("Стоимость выбранных акций: ")
            for stock in events["stocks_prices"]:
                print(f"Акция: {stock["stock"]}")
                print(f"Стоимость: {stock["price"]}")
                print("-" * 40)
        elif selected_section == "3":
            choose_report = input(
                """Какой отчёт сформировать?
(Во всех отчетах, если не указывать дату, формирование отчета будет за последние 3 месяца до сегодняшнего дня)
1 - Траты по категории за последие 3 месяца до указаной даты
2 - средние траты по дням недели за последние 3 месяца до указанной даты
3 - средние траты по выходным и будням за последние 3 месяца до указаной даты
-> """
            )
            while choose_report not in ("1", "2", "3"):
                choose_report = input("Выберите из : 1 2 3 -> ")
            date = input("Введите дату в формате 2025-01-01 00:00:00 или нажмите Enter для пропуска даты -> ")
            file: str | None = input(
                "Введите название файла для отчета(Нажмите enter, если не хотите указывать название) -> "
            )
            file = file + ".xlsx" if file else None
            if file:
                if choose_report == "1":
                    category = input("Введите категорию для поиска: ")
                    write_to_file(file)(spending_by_category)(df, category, date or None)
                elif choose_report == "2":
                    write_to_file(file)(spending_by_weekday)(df, date or None)
                elif choose_report == "3":
                    write_to_file(file)(spending_by_workday)(df, date or None)
                print("Пожалуйста, ожидайте, отчет формируется и скоро появится в корневой папке.")
                print("=" * 40)
            else:
                if choose_report == "1":
                    category = input("Введите категорию для поиска: ")
                    write_to_file()(spending_by_category)(df, category, date or None)
                elif choose_report == "2":
                    write_to_file()(spending_by_weekday)(df, date or None)
                elif choose_report == "3":
                    write_to_file()(spending_by_workday)(df, date or None)
                print("Пожалуйста, ожидайте, отчет формируется и скоро появится в корневой папке.")
                print("=" * 40)
        elif selected_section == "4":
            choose_service = input(
                """Каким сервисом хотите воспользоваться?
1 - Анализ выгоды, полученной от кэшбэка
2 - Анализ данных о потенциальном накоплении через инвесткопилку
3 - Поиск операций по указанному слову
4 - Поиск операций, в которых указан номер телефона
5 - Поиск переводов физическим лицам          
"""
            )
            while choose_service not in ("1", "2", "3", "4", "5"):
                choose_report = input("Выберите из : 1 2 3 4 5-> ")

            if choose_service == "1":
                print("=" * 40)
                year = input("Введите год для анализа: ")
                month = input("Введите месяц для анализа: ")
                print("=" * 40)
                cashback = json.loads(profitable_cashback(df_list_of_dicts, year, month))
                for category, amount in cashback.items():
                    print(f"Категория : {category}\nСумма: {amount}")
                    print("-" * 40)
                print("=" * 40)

            elif choose_service == "2":
                print("=" * 40)
                month = input("Введите год и месяц для анализа в формате 2020-02")
                limit = input("Введите лимит для округления суммы")
                print("=" * 40)
                investment_check = investment_bank(month, df_list_of_dicts, limit)
                print(f"За {month} с округлением {limit} сумма накоплений составляет {investment_check}")
                print("=" * 40)

            elif choose_service == "3":
                print("=" * 40)
                string_for_search = input("Введите слово для поиска в описаниях и категориях: ")
                matched_operations = json.loads(simple_search(df_list_of_dicts, string_for_search))
                print("=" * 40)
                for operation in matched_operations:
                    print(
                        f"""Дата операции : {operation["Дата операции"]}
Сумма операции : {operation["Сумма операции"]}
Номер карты: {operation["Сумма операции"]}
Категория: {operation["Категория"]}
Описание: {operation["Описание"]}"""
                    )
                    print("-" * 40)
                print("=" * 40)

            elif choose_service == "4":
                print("=" * 40)
                for operation in json.loads(phone_number_search(df_list_of_dicts)):
                    print(
                        f"""Дата операции : {operation["Дата операции"]}
Сумма операции : {operation["Сумма операции"]}
Номер карты: {operation["Сумма операции"]}
Категория: {operation["Категория"]}
Описание: {operation["Описание"]}"""
                    )
                    print("-" * 40)
                print("=" * 40)

            elif choose_service == "5":
                print("=" * 40)
                for operation in json.loads(remittance_search(df_list_of_dicts)):
                    print(
                        f"""Дата операции : {operation["Дата операции"]}
Сумма операции : {operation["Сумма операции"]}
Номер карты: {operation["Сумма операции"]}
Категория: {operation["Категория"]}
Описание: {operation["Описание"]}"""
                    )
                    print("-" * 40)
                print("=" * 40)

        elif selected_section == "5":
            break


# print(main_page("2019-11-11 00:00:00"))
main()
