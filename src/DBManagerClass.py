import logging
from re import search

import psycopg2

from src.utils import validate_salary


class DBManager:
    """ Класс для работы с базой данных. """

    def __init__(self, conn, cur) -> None:
        """
        Конструктор класса. Сохраняет объекты подключения и курсора для базы данных,
        а также список кортежей, в который сохраняется результат запросов
        на выборку из базы данных для последующего отображения в консоли,
        и при желании Пользователя записи данных во внешний excel файл.
        """
        self.conn = conn
        self.cur = cur
        self.result: list[tuple] = []  # будем сохранять выборку данных, если потребуется ее сохранить в файл

    def create_database(self, params, db_name) -> None:
        """ Метод создает базу данных Работодателей. """
        self.conn = psycopg2.connect(**params)
        self.conn.autocommit = True
        self.cur = self.conn.cursor()

        try:
            self.cur.execute(f'DROP DATABASE IF EXISTS {db_name}')
            print('Создаю базу данных с работодателями и вакансиями...')
            self.cur.execute(f'CREATE DATABASE {db_name}')
            logging.info(f"База данных '{db_name}' успешно создана.")

        except psycopg2.Error as e:
            logging.error(f"Ошибка при создании базы данных: {e}")

        self.conn.commit()

        self.cur.close()
        self.conn.close()

    def create_tables(self) -> None:
        """ Метод создает новые таблицы в базе данных. """
        create_companies_table = """
            CREATE TABLE companies (
                company_id SERIAL PRIMARY KEY,
                company_title VARCHAR(255) NOT NULL
            )
        """
        self.cur.execute(create_companies_table)

        create_vacancies_table = """
            CREATE TABLE IF NOT EXISTS vacancies (
                vacancy_id SERIAL PRIMARY KEY,
                company_id INT REFERENCES companies(company_id),
                vacancy_name VARCHAR(200),
                salary INT,
                url VARCHAR(200)
            )
        """
        print('Создаю таблицы в базе данных...')
        self.cur.execute(create_vacancies_table)

        self.conn.commit()
        logging.info("Таблицы 'companies' и 'vacancies' успешно созданы.")

    def save_to_database(self, vacancies) -> None:
        """ Метод вносит новые записи в таблицы. """
        for employer in vacancies:
            employer_name = list(employer.keys())[0]  # сохраняем имя Работодателя
            self.cur.execute(
                "INSERT INTO  companies (company_title) VALUES ('%s') RETURNING company_id" % str(employer_name))
            logging.info(f'Данные по работодателю {employer_name} внесены в БД.')
            company_id = self.cur.fetchone()[0]  # сохраняем номер id компании для последующего использования
            for vacancy in employer[employer_name]:  # итерируемся по списку вакансий конкретного Работодателя
                name = vacancy.get('name')
                salary = max(validate_salary(vacancy, 'from'), validate_salary(vacancy, 'to'))
                url = vacancy.get('alternate_url')

                self.cur.execute(
                    """
                    INSERT INTO vacancies (company_id, vacancy_name, salary, url)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (company_id, name, salary, url)
                )
            self.conn.commit()
            logging.info(f'Данные по вакансиям работодателям {employer_name} внесены в БД.')

    def get_companies_and_vacancies_count(self) -> None:
        """ Метод получает список всех компаний и количество вакансий у каждой компании. """
        query = """
            SELECT company_title, COUNT(vacancy_name) as vacancies
            FROM companies JOIN vacancies USING(company_id)
            GROUP BY company_title
        """
        self.cur.execute(query)
        logging.info('Выполнен запрос на получение списка всех компаний и их вакансий из базы данных.')
        self.result = self.cur.fetchall()
        print()
        for row in self.result:
            # форматируем вывод, обрезаем до 20 символов, выравниваем влево и добавляем недостающие пробелы
            print(f'Компания: {row[0][:15].ljust(15)} | кол-во вакансий: {row[1]}')
        print('Нажмите Enter для продолжения...')
        input()

    def get_all_vacancies(self) -> None:
        """
        Метод получает список всех вакансий с указанием названия компании,
        названия вакансии, зарплаты и ссылки на вакансию.
        """
        query = """
            SELECT company_title, vacancy_name, salary, url
            FROM companies
            JOIN vacancies USING(company_id)
        """
        self.cur.execute(query)
        logging.info('Выполнен запрос на получение всех вакансий, зарплаты и ссылки на вакансию.')
        self.result = self.cur.fetchall()
        print()
        for row in self.result:
            salary = str(row[2]).ljust(10) if row[2] else 'не указана'.ljust(10)
            # форматируем вывод, обрезаем до нужного количества символов, выравниваем влево и добавляем недостающие пробелы
            print(
                f'Компания: {row[0][:15].ljust(15)} | вакансия: {row[1][:50].ljust(50)} | зарплата: {salary} | ссылка: {row[3]}')
        print('Нажмите Enter для продолжения...')
        input()

    def get_avg_salary(self) -> None:
        """ Метод получает среднюю зарплату по компаниям. """
        query = """
            SELECT company_title, ROUND(AVG(salary), 2)
            FROM companies JOIN vacancies USING(company_id)
            WHERE salary <> 0
            GROUP BY company_title
        """
        self.cur.execute(query)
        logging.info('Выполнен запрос на получение средней зарплаты по компании.')
        self.result = self.cur.fetchall()
        print()
        for row in self.result:
            # форматируем вывод, обрезаем до нужного количества символов, выравниваем влево и добавляем недостающие пробелы
            print(
                f'Компания: {row[0][:15].ljust(15)} | средняя зарплата: {row[1]}')
        print('Нажмите Enter для продолжения...')
        input()

    def get_vacancies_with_higher_salary(self) -> None:
        """ Метод получает список всех вакансий, у которых зарплата выше средней по всем вакансиям. """
        query = """
            SELECT company_title, vacancy_name, salary, url
            FROM companies
            JOIN vacancies USING(company_id)
            WHERE salary > (
                SELECT ROUND(AVG(salary), 2)
                FROM vacancies
                WHERE salary <> 0)
        """
        self.cur.execute(query)
        logging.info(
            'Выполнен запрос на получение списка всех вакансий, у которых зарплата выше средней по всем вакансиям.')
        self.result = self.cur.fetchall()
        print()
        for row in self.result:
            # форматируем вывод, обрезаем до нужного количества символов, выравниваем влево и добавляем недостающие пробелы
            print(
                f'Компания: {row[0][:15].ljust(15)} | вакансия: {row[1][:50].ljust(50)} | зарплата: {str(row[2]).ljust(10)} | ссылка: {row[3]}')
        print('Нажмите Enter для продолжения...')
        input()

    def get_vacancies_with_keyword(self):
        """ Метод получает список всех вакансий, в названии которых содержатся переданные в метод слова. """
        search_word = input('Введите слово для поиска в наименовании вакансии (регистр имеет значение): ')
        query = f"""
            SELECT company_title, vacancy_name, salary, url
            FROM companies
            JOIN vacancies USING(company_id)
            WHERE vacancy_name LIKE '%{search_word}%'
        """
        self.cur.execute(query)
        logging.info(
            f'Выполнен запрос на получение списка всех вакансий, в названии которых встречается слово {search_word}.')
        self.result = self.cur.fetchall()
        print()
        for row in self.result:
            salary = str(row[2]).ljust(10) if row[2] else 'не указана'.ljust(10)
            # форматируем вывод, обрезаем до нужного количества символов, выравниваем влево и добавляем недостающие пробелы
            print(
                f'Компания: {row[0][:15].ljust(15)} | вакансия: {row[1][:50].ljust(50)} | зарплата: {salary} | ссылка: {row[3]}')
        print('Нажмите Enter для продолжения...')
        input()

    def execute_query(self, query, out_string) -> list[tuple]:
        """ Метод исполняет запрос на выборку и сохраняет получение данные в виде списка кортежей. """
        self.cur.execute(query)
        result = self.cur.fetchall()
        print()
        [print(out_string) for _ in result]
        # for row in result:
        #     print(out_string)
        print('Нажмите Enter для продолжения...')
        input()
        return result
