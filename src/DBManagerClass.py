import logging
from typing import Any

import psycopg2

from src.utils import validate_salary


class DBManager:
    """ Класс для работы с базой данных. """

    def __init__(self, conn: Any, cur: Any) -> None:
        """
        Конструктор класса. Сохраняет объекты подключения и курсора для базы данных,
        а также список кортежей, в который сохраняется результат запросов
        на выборку из базы данных для последующего отображения в консоли,
        и при желании Пользователя записи данных во внешний excel файл.
        """
        self.conn = conn
        self.cur = cur
        self.query: str = ''
        self.result: list[tuple] = []  # будем сохранять выборку данных, если потребуется ее сохранить в excel файл
        self.columns: list[str] = []  # будем названия столбцов, если потребуется выборку в excel файл

        """
        Cловарь self.data необходим для того, чтобы сохранять индексы при обращении к результатам запросов,
        которые хранятся в self.results в виде списка кортежей.
        Этот словарь используется при форматировании вывода в консоль.
        Так как элементов в кортеже может быть всегда разное в зависимости от запроса,
        то индексы необходимо обнулять после запрос и перед выводом в консоль.
        """
        self.data = {
            'company': 0,
            'vacancy': 0,
            'vacancy_count': 0,
            'salary': 0,
            'avg_salary': 0,
            'url': 0,
        }

    def create_database(self, params: dict, db_name: str) -> None:
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
        self.query = """
            CREATE TABLE companies (
                company_id SERIAL PRIMARY KEY,
                company_title VARCHAR(255) NOT NULL
            )
        """
        self.cur.execute(self.query)

        self.query = """
            CREATE TABLE IF NOT EXISTS vacancies (
                vacancy_id SERIAL PRIMARY KEY,
                company_id INT REFERENCES companies(company_id),
                vacancy_name VARCHAR(200),
                salary INT,
                url VARCHAR(200)
            )
        """
        print('Создаю таблицы в базе данных...')
        self.cur.execute(self.query)

        self.conn.commit()
        logging.info("Таблицы 'companies' и 'vacancies' успешно созданы.")

    def save_to_database(self, vacancies: list[dict]) -> None:
        """ Метод вносит новые записи в таблицы. """
        for employer in vacancies:
            employer_name = list(employer.keys())[0]  # сохраняем имя Работодателя
            self.cur.execute(
                "INSERT INTO  companies (company_title) VALUES ('%s') RETURNING company_id" % str(employer_name))
            logging.info(f'Данные по работодателю {employer_name} внесены в БД.')
            company_id = self.cur.fetchone()[0]  # сохраняем номер id компании для последующего использования
            for vacancy in employer[employer_name]:  # итерируемся по списку вакансий конкретного Работодателя
                name = vacancy.get('name')
                salary_int = max(validate_salary(vacancy, 'from'), validate_salary(vacancy, 'to'))
                url = vacancy.get('alternate_url')

                self.cur.execute(
                    """
                    INSERT INTO vacancies (company_id, vacancy_name, salary, url)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (company_id, name, salary_int, url)
                )
            self.conn.commit()
            logging.info(f'Данные по вакансиям работодателям {employer_name} внесены в БД.')

    def get_companies_and_vacancies_count(self) -> None:
        """ Метод получает список всех компаний и количество вакансий у каждой компании. """
        self.query = """
            SELECT company_title, COUNT(vacancy_name) as vacancies
            FROM companies JOIN vacancies USING(company_id)
            GROUP BY company_title
        """
        self.columns = ['Компания', 'Кол-во вакансий']
        self.execute_query('Выполнен запрос на получение списка всех компаний и их вакансий из базы данных.')

        # оставляем компанию (0), кол-во вакансий (1)
        # остальное обнуляем для последующих запросов
        self.update_data_indexes([0, 1, 0, 0, 0, 0])

        self.format_output('Компания: {company} | кол-во вакансий: {vacancy_count}')

    def get_all_vacancies(self) -> None:
        """
        Метод получает список всех вакансий с указанием названия компании,
        названия вакансии, зарплаты и ссылки на вакансию.
        """
        self.query = """
            SELECT company_title, vacancy_name, salary, url
            FROM companies
            JOIN vacancies USING(company_id)
        """
        self.columns = ['Компания', 'Вакансия', 'Зарплата', 'URL']
        self.execute_query('Выполнен запрос на получение всех вакансий, зарплаты и ссылки на вакансию.')

        # оставляем компанию (0), вакансию (1), зарплату (2) и url(3)
        # остальное обнуляем для последующих запросов
        self.update_data_indexes([0, 0, 1, 2, 0, 3])

        self.format_output('Компания: {company} | вакансия: {vacancy} | зарплата: {salary} | ссылка: {url}')

    def get_avg_salary(self) -> None:
        """ Метод получает среднюю зарплату по компаниям. """
        self.query = """
            SELECT company_title, ROUND(AVG(salary), 2)
            FROM companies JOIN vacancies USING(company_id)
            WHERE salary <> 0
            GROUP BY company_title
        """
        self.columns = ['Компания', 'Средняя зарплата']
        self.execute_query('Выполнен запрос на получение средней зарплаты по компании.')

        # оставляем компанию (0) и среднюю зарплату (1)
        # остальное обнуляем для последующих запросов
        self.update_data_indexes([0, 0, 0, 0, 1, 0])

        self.format_output('Компания: {company} | средняя зарплата: {avg_salary}')

    def get_vacancies_with_higher_salary(self) -> None:
        """ Метод получает список всех вакансий, у которых зарплата выше средней по всем вакансиям. """
        self.query = """
            SELECT company_title, vacancy_name, salary, url
            FROM companies
            JOIN vacancies USING(company_id)
            WHERE salary > (
                SELECT ROUND(AVG(salary), 2)
                FROM vacancies
                WHERE salary <> 0)
        """
        self.columns = ['Компания', 'Вакансия', 'Зарплата', 'URL']
        self.execute_query(
            'Выполнен запрос на получение списка всех вакансий, у которых зарплата выше средней по всем вакансиям.')

        # оставляем компанию (0), вакансию (1), зарплату (2) и url(3)
        # остальное обнуляем для последующих запросов
        self.update_data_indexes([0, 0, 1, 2, 0, 3])

        self.format_output('Компания: {company} | вакансия: {vacancy} | зарплата: {salary} | ссылка: {url}')

    def get_vacancies_with_keyword(self) -> None:
        """ Метод получает список всех вакансий, в названии которых содержатся переданные в метод слова. """
        search_word = input('Введите слово для поиска в наименовании вакансии (регистр имеет значение): ')
        self.query = f"""
            SELECT company_title, vacancy_name, salary, url
            FROM companies
            JOIN vacancies USING(company_id)
            WHERE vacancy_name LIKE '%{search_word}%'
        """
        self.columns = ['Компания', 'Вакансия', 'Зарплата', 'URL']
        self.execute_query(
            f'Выполнен запрос на получение списка всех вакансий, в названии которых встречается слово "{search_word}".')

        # оставляем компанию (0), вакансию (1), зарплату (2) и url(3)
        # остальное обнуляем для последующих запросов
        self.update_data_indexes([0, 0, 1, 2, 0, 3])

        self.format_output('Компания: {company} | вакансия: {vacancy} | зарплата: {salary} | ссылка: {url}')

    def execute_query(self, log_message: str) -> None:
        """ Метод исполняет запрос на выборку и сохраняет получение данные в виде списка кортежей. """
        self.cur.execute(self.query)
        logging.info(log_message)
        self.result = self.cur.fetchall()

    def format_output(self, output_string: str) -> None:
        """ Метод форматирует вывод данных в консоль. """
        print()
        for row in self.result:
            try:
                salary = str(row[self.data['salary']]).ljust(10) if row[self.data['salary']] else 'не указана'.ljust(10)
            except Exception:
                salary = 'не указана'

            data_to_output = {
                'company': row[self.data['company']][:15].ljust(15),
                'vacancy_count': row[self.data['vacancy_count']],
                'vacancy': row[self.data['vacancy']][:50].ljust(50),
                'salary': salary,
                'avg_salary': str(row[self.data['avg_salary']]),
                'url': row[self.data['url']]
            }

            print(output_string.format(**data_to_output))
        print('Нажмите Enter для продолжения...')
        input()

    def update_data_indexes(self, list_of_indexes: list[int]) -> None:
        " Метод обновляет индексы в словаре для избежания ошибки адресации в запросах при выводе в консоль. "
        self.data['company'] = list_of_indexes[0]
        self.data['vacancy_count'] = list_of_indexes[1]
        self.data['vacancy'] = list_of_indexes[2]
        self.data['salary'] = list_of_indexes[3]
        self.data['avg_salary'] = list_of_indexes[4]
        self.data['url'] = list_of_indexes[5]
