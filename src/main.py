import logging

import psycopg2

from src.config import config

import requests
from src.constants import employers

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


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


def create_tables(params: dict, database_name='my_database') -> None:
    conn = psycopg2.connect(**params, dbname=database_name)

    with conn.cursor() as cur:
        create_companies_table = """
            CREATE TABLE companies (
                company_id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL
            )
        """
        cur.execute(create_companies_table)

        create_vacancies_table = """
            CREATE TABLE IF NOT EXISTS vacancies (
                vacancy_id SERIAL PRIMARY KEY,
                company_id INT REFERENCES companies(company_id),
                title VARCHAR(200),
                salary VARCHAR(50),
                url VARCHAR(200)
            )
        """
        cur.execute(create_vacancies_table)

    conn.commit()
    conn.close()
    logging.info("Таблицы 'companies' и 'vacancies' успешно созданы.")


def get_companies_and_vacancies_count(employer_id):
    url_get_num_vac = f'https://api.hh.ru/employers/{employer_id}'
    number_of_vacs = requests.get(url_get_num_vac).json()['open_vacancies']

    return number_of_vacs


def get_all_vacancies(employer_id, vacancy_amount):
    url_vacancies = f'https://api.hh.ru/vacancies?employer_id={employer_id}'
    for vac in vacancy_amount:
        vacancy = requests.get(url_vacancies).json()
        # print(vacancy[])
        input()


def main():
    params = config()
    db_name = 'top_employers'
    create_database(params, db_name)
    create_tables(params, db_name)


if __name__ == '__main__':
    main()
