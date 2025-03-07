import logging
import time

import psycopg2

from src.config import config

import requests
from src.constants import employers

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class EmployerVacancy:
    """ Класс для работы с API сайта hh.ru. """
    __slots__ = ('url', 'headers', 'params', 'vacancies', 'employer_id')

    def __init__(self, employer_id: str) -> None:
        self.url = f'https://api.hh.ru/vacancies?employer_id={employer_id}'
        self.headers: dict = {'User-Agent': 'HH-User-Agent'}
        self.params: dict = {'page': 0, 'per_page': 25}
        self.vacancies: list[dict] = []
        self.employer_id = employer_id

    def load_vacancies(self) -> None:
        """ Метод получения вакансий с сайта. """
        while self.params.get('page') != 20:
            response = requests.get(self.url, headers=self.headers, params=self.params)
            if response.status_code == 200:
                vacancies = response.json()["items"]
                self.vacancies.extend(vacancies)
            else:
                print("  Что-то пошло не так с запросом, ошибка:", response.status_code)
            self.params['page'] += 1
            print("\rЗагружаю вакансии с сайта hh.ru. Завершено:", str(self.params['page'] * 100 // 20) + "%",
                  end="")
            time.sleep(0.3)
        print()


def create_database(params: dict, db_name: str = 'database') -> None:
    """ Создание базы данных Работодателей. """
    conn = psycopg2.connect(**params)
    conn.autocommit = True
    cur = conn.cursor()
    try:
        cur.execute(f'DROP DATABASE IF EXISTS {db_name}')
        cur.execute(f'CREATE DATABASE {db_name}')
        logging.info(f"База данных '{db_name}' успешно создана.")

    except psycopg2.Error as e:
        logging.error(f"Ошибка при создании базы данных: {e}")

    cur.close()
    conn.close()


def intro():
    """ Приветствие Пользователя и описание работы программы. """
    print('\n' + "#" * 75)
    print("Добро пожаловать в программу получения и обработки вакансий с сайта hh.ru.\n"
          "Программа позволяет получить набор вакансий (до 500) по десяти компаниям\n"
          "и записать их в базу данных.")
    print("#" * 75)
    print('Вакансии будут найдены для следующих компаний:')
    [print(employer) for employer in employers]


def create_tables(params: dict, database_name='my_database') -> None:
    conn = psycopg2.connect(**params, dbname=database_name)

    with conn.cursor() as cur:
        create_companies_table = """
            CREATE TABLE companies (
                company_id SERIAL PRIMARY KEY,
                company_title VARCHAR(255) NOT NULL
            )
        """
        cur.execute(create_companies_table)

        create_vacancies_table = """
            CREATE TABLE IF NOT EXISTS vacancies (
                vacancy_id SERIAL PRIMARY KEY,
                company_id INT REFERENCES companies(company_id),
                vacancy_name VARCHAR(200),
                salary VARCHAR(50),
                url VARCHAR(200)
            )
        """
        cur.execute(create_vacancies_table)

    conn.commit()
    conn.close()
    logging.info("Таблицы 'companies' и 'vacancies' успешно созданы.")


def get_companies_and_vacancies_count():
    pass


def get_all_vacancies(employer_id: str):
    pass


def save_to_database(params: dict, vacancies: list[dict], database_name: str) -> None:
    conn = psycopg2.connect(dbname=database_name, **params)

    with conn.cursor() as cur:
        for employer in vacancies:
            employer_name = list(employer.keys())[0]  # сохраняем имя Работодателя
            # print(employer_name)
            cur.execute(
                "INSERT INTO  companies (company_title) VALUES ('%s') RETURNING company_id" % str(employer_name))
            logging.info(f'Данные по работодателю {employer_name} внесены в БД.')
            company_id = cur.fetchone()[0]
            # print(company_id)
            for vacancy in employer[employer_name]:  # итерируемся по списку вакансий конкретного Работодателя
                name = vacancy.get('name')
                salary = max(validate_salary(vacancy, 'from'), validate_salary(vacancy, 'to'))
                url = vacancy.get('alternate_url')

                cur.execute(
                    """
                    INSERT INTO vacancies (company_id, vacancy_name, salary, url)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (company_id, name, salary, url)
                )
            conn.commit()
            logging.info(f'Данные по вакансиям работодателям {employer_name} внесены в БД.')

    conn.close()


def validate_salary(vacancy: dict, param_to_check: str) -> int:
    """ Класс-метод проверяет на валидность значения полей Зарплаты. """
    try:
        salary = int(vacancy['salary'][param_to_check])
    except Exception:
        salary = 0
    return salary


def main() -> None:
    """ Основная функция программы. """

    intro()
    employers_vacancies = []
    for name, id_ in employers.items():
        emp = EmployerVacancy(id_)
        print(f'\nЗагружаю вакансии для: {name}')
        emp.load_vacancies()
        employers_vacancies.append({name: emp.vacancies})
        del emp

    params = config()
    db_name = 'top_employers'
    create_database(params, db_name)
    create_tables(params, db_name)
    save_to_database(params, employers_vacancies, db_name)


if __name__ == '__main__':
    main()
