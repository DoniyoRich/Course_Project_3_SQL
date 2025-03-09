import logging

import psycopg2

from src.config import config
from src.constants import DB_NAME, EMPLOYERS, LOGS_DIR, USER_MENU_LIST
from src.DBManagerClass import DBManager
from src.EmployerVacancyClass import EmployerVacancy
from src.ExcelSaver import ExcelSaver
from src.utils import intro, user_menu

# Настраиваем логирование на вывод логов в файл
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.FileHandler(LOGS_DIR + 'logs.log', 'w', encoding='UTF-8')]
)


def main() -> None:
    """ Основная функция программы. Взаимодействие с Пользователем. """

    intro()

    # в списке будем собирать названия Работодателей с их вакансиями
    # ограничимся до 500 вакансий в контексте учебного проекта
    employers_vacancies = []
    for name, id_ in EMPLOYERS.items():
        emp = EmployerVacancy(id_)
        print(f'\nЗагружаю вакансии для: {name}')
        emp.load_vacancies()
        employers_vacancies.append({name: emp.vacancies})
        del emp

    # данные для подключения к базе данных
    params = config()

    # создаем базу данных Работодателей,
    # предварительно подключившись к базе данных postgresql
    with psycopg2.connect(**params) as conn:
        with conn.cursor() as cur:
            db_create = DBManager(conn, cur)
            db_create.create_database(params, DB_NAME)
            # удалим объект, он нам больше не понадобится
            del db_create

    # теперь подключаемся к созданной базе данных Работодателей и дальше работаем с этим подключением
    with psycopg2.connect(dbname=DB_NAME, **params) as conn:
        with conn.cursor() as cur:

            db = DBManager(conn, cur)
            db.create_tables()
            db.save_to_database(employers_vacancies)

            user_choice = -1
            while user_choice != 0:
                user_choice = user_menu(USER_MENU_LIST)
                match user_choice:
                    case 0:
                        print("\nХорошего дня! ;)")
                        logging.info('Завершение работы программы.')
                        break
                    case 1:
                        db.get_companies_and_vacancies_count()
                    case 2:
                        db.get_all_vacancies()
                    case 3:
                        db.get_avg_salary()
                    case 4:
                        db.get_vacancies_with_higher_salary()
                    case 5:
                        db.get_vacancies_with_keyword()
                    case 6:
                        # сохраняем в excel файл
                        while True:
                            try:
                                filename = input('Введите имя файла: ')
                                excel_saver = ExcelSaver()
                                excel_saver.save_to_file(db.result, db.columns, filename)
                                break
                            except Exception:
                                continue


# Точка входа в приложение
if __name__ == '__main__':
    main()
