from src.constants import EMPLOYERS


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
