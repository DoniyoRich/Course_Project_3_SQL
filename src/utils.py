import os
from typing import Any

from src.constants import EMPLOYERS, YES_NO_CHOICE


def intro():
    """ Приветствие Пользователя и описание работы программы. """
    print('\n' + "#" * 75)
    print("Добро пожаловать в программу получения и обработки вакансий с сайта hh.ru.\n"
          "Программа позволяет получить набор вакансий (до 500) по десяти компаниям\n"
          "и записать их в базу данных.")
    print("#" * 75)
    print('Вакансии будут найдены для следующих компаний:')
    [print('-', employer) for employer in EMPLOYERS]


def validate_salary(vacancy: dict, param_to_check: str) -> int:
    """ Класс-метод проверяет на валидность значения полей Зарплаты. """
    try:
        salary = int(vacancy['salary'][param_to_check])
    except Exception:
        salary = 0
    return salary


def user_menu(menu_list: list[str]) -> int:
    """ Функция возвращает целое число - выбор Пользователя. """
    user_choice = -1
    while user_choice not in list(range(len(menu_list))):
        print('\nВыберите действие:\n')
        [print(menu_item) for menu_item in menu_list]
        try:
            user_choice = int(input('Ваш выбор: '))
        except Exception:
            print('Пожалуйста, введите число из списка..')
            continue
    return user_choice


# def convert_to_list(vacancies: list[Any]) -> list[dict]:
#     """ Функция создает список словарей вакансий из списка объектов вакансий. """
#     vacancies_list = [
#         {'ID': int(vacancy.id_num),
#          'должность': vacancy.name,
#          'регион': vacancy.area,
#          'зарплата': vacancy.salary,
#          'требуемый опыт': vacancy.experience,
#          'ссылка на вакансию': vacancy.alt_url}
#         for vacancy in vacancies
#     ]
#     return vacancies_list


# def saving_file(vacancies: list[Any], file_type: str, saver: Any) -> None:
#     """
#     Функция вызывает метод сохранения в файл json или excel
#     в зависимости от поступившего на вход объекта и типа расширения файла.
#     """
#     filename = input(f"Введите имя {file_type} файла: ")
#     file_vacancies = convert_to_list(vacancies)
#     saver.save_to_file(file_vacancies, os.path.join(DATA_DIR, filename))
#     ext = '.json'
#     if file_type == 'Excel':
#         ext = '.xlsx'
#     print(f'Файл "{filename}{ext}" сохранен.')


# def ask_to_save(obj: object, filtered: list[Any]) -> None:
#     """
#     Функция запрашивает у Пользователя о необходимости сохранения выборки
#     после произведенных операций с набором данных.
#     """
#     print("Сохранить выборку для дальнейшей работы?")
#     if user_menu(YES_NO_CHOICE) == 1:
#         setattr(obj, 'vacancies', filtered)
#         print("Выборка сохранена.")
#     else:
#         print("Выборка не сохранена.")


# def output_to_console(vacancies: list[object]) -> None:
#     """ Вывод вакансий в консоль. Задается количество выводимых вакансий за один раз. """
#     print(f"Осталось вакансий: {len(vacancies)}")
#     quantity = 1
#     while isinstance(quantity, int):
#         try:
#             quantity = int(input("\nСколько вакансий выводить за один раз?: "))
#             if quantity > 0:
#                 break
#         except Exception:
#             continue
#     if len(vacancies):
#         print(f"Будет выводиться по {quantity} вакансий за раз. Для продолжения нажимайте Enter\n")
#         count = round(len(vacancies) / quantity)
#         start, end = 0, quantity
#         while count >= 0:
#             input()
#             [print(vacancy) for vacancy in vacancies[start:end]]
#             start += quantity
#             end += quantity
#             count -= 1
#     else:
#         print("Вакансий нет")
