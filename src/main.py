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
            time.sleep(0.5)


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


def get_all_vacancies(employer_id: str):
    url_vacancies = f'https://api.hh.ru/vacancies?employer_id={employer_id}'
    vacancies = requests.get(url_vacancies).json()['items']
    vacancies_short = []
    for vac in vacancies:
        vacancies_short.append(
            {'Должность': vac['name'], 'Зарплата': vac.get('salary'), 'Сссылка на вакансию': vac.get('alternate_url')})
    print(vacancies_short)
    # print(vacancies)
    # vacancy_list = []
    # for vac in vacancies:
    #     vacancy_list.append()
    #     print(vacancy[])
    # input()


def save_to_database(params: dict, vacancies: list[dict], database_name: str) -> None:
    conn = psycopg2.connect(dbname=database_name, **params)

    with conn.cursor() as cur:
        for employer in vacancies:
            employer_name = vacancies[0]
            cur.execute(
                """
                INSERT INTO channels (title, views, subscribers, videos, channel_url)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING channel_id
                """,
                (channel_data['title'], channel_stats['viewCount'], channel_stats['subscriberCount'],
                 channel_stats['videoCount'], f"https://www.youtube.com/channel/{channel['channel']['id']}")
            )
            channel_id = cur.fetchone()[0]
            videos_data = channel['videos']
            for video in videos_data:
                video_data = video['snippet']
                cur.execute(
                    """
                    INSERT INTO videos (channel_id, title, publish_date, video_url)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (channel_id, video_data['title'], video_data['publishedAt'],
                     f"https://www.youtube.com/watch?v={video['id']['videoId']}")
                )


def main() -> None:
    """ Основная функция программы. """

    # создаем словарь с названием компаний и количеством их открытых вакансий
    # number_of_vacs = {name: get_companies_and_vacancies_count(id_) for name, id_ in employers.items()}
    # get_companies_and_vacancies_count(employer_id)
    # employers_vacancies = {}
    # for name, id_ in employers.items():
    #     employers_vacancies[name] = get_companies_and_vacancies_count(id_)
    # print(employers_vacancies)
    # get_all_vacancies(id_)
    # for employers_vacancy in
    # number_of_vacs.append(get_companies_and_vacancies_count(employer_id))

    intro()
    employers_vacancies = []
    for name, id_ in employers.items():
        emp = EmployerVacancy(id_)
        print(f'\nЗагружаю вакансии для: {name}')
        emp.load_vacancies()
        employers_vacancies.append({name: emp.vacancies})

    params = config()
    db_name = 'top_employers'
    # create_database(params, db_name)
    # create_tables(params, db_name)
    save_to_database(params, employers_vacancies, db_name)


if __name__ == '__main__':
    main()
