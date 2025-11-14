#Отображение главной страницы, а потом меню выбора разделов и чтобы выбрать раздел - нужно это делать с меню выбора разделов
# Выбор разделов в бесконечном цикле, после континью будет это меню, после брейк выход из приложения
# В меню по цифрам будет расположены разделы, к примеру раздел 1 - главная, вызывает главную функцию, 2 - остальное и тд
from src.views import main_page, show_main_page
import datetime
import pandas as pd
from utils.functions import operations_reader
import json

NOW_TIME = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
TIME_FOR_TEST = "2019-11-11 00:00:00"
path = r"data\operations.xlsx"
df = operations_reader(path)
readed_file = df if df is not None and not df.empty else pd.DataFrame()


def main():
    #main_page start
    show_main_page(TIME_FOR_TEST)

    #menu start
    print("""Для перехода в раздел, выберите номер, соответствующий разделу: 
1 -  «Главная»
2 -  «События»
3 -  «Отчёты»
4 -  «Сервисы»
5 -  Выйти из приложения
""")
    while True:
        selected_section = input("Ваш выбор: ")
        while selected_section not in ("1", "2", "3", "4", "5"):
            selected_section = input("Ваш выбор: ")



#print(main_page("2019-11-11 00:00:00"))
main()