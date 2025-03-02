# import os
# from dotenv import load_dotenv
import logging

import psycopg2
from psycopg2 import sql

import config

import requests
from constants import employers

DB_CONFIG = {
    'dbname': 'postgres',
    'host': 'localhost',
    'port': '5432',
    'user': 'postgres',
    'password': '12345678'
}

# from src.DBManagerClass import DBManager
#
# load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def create_table(conn):
    cursor = conn.cursor()

    create_table_query = """
        CREATE TABLE IF NOT EXISTS vacancies (
            id SERIAL PRIMARY KEY,
            city VARCHAR(50),
            company VARCHAR(200),
            industry VARCHAR(200),
            title VARCHAR(200),
            keywords TEXT,
            skills TEXT,
            experience VARCHAR(50),
            salary VARCHAR(50),
            url VARCHAR(200)
        )
    """
    cursor.execute(create_table_query)

    conn.commit()
    cursor.close()
    logging.info("Таблица 'vacancies' успешно создана.")


def create_database(db_name: str = 'database'):
    global conn, cur
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True  # autocommit для выполнения CREATE DATABASE
        cur = conn.cursor()

        cur.execute('CREATE DATABASE {}'.format(db_name))
        logging.info(f"База данных '{db_name}' успешно создана.")

    except psycopg2.Error as e:
        logging.error(f"Ошибка при создании базы данных: {e}")

    finally:
        if conn:
            cur.close()
            conn.close()


def main():
    # api_key_hh = os.getenv('API_KEY_HH')
    # print(api_key_hh)
    create_database('top_employers')


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


if __name__ == '__main__':
    main()
