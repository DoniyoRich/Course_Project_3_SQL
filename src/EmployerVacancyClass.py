import time

import requests


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
        """ Метод получения вакансий с сайта hh.ru. """
        while self.params.get('page') != 20:
            response = requests.get(self.url, headers=self.headers, params=self.params)
            if response.status_code == 200:
                vacancies = response.json()["items"]
                self.vacancies.extend(vacancies)
            else:
                print("  Что-то пошло не так с запросом, ошибка:", response.status_code)
            self.params['page'] += 1
            print("\rЗавершено:", str(self.params['page'] * 100 // 20) + "%",
                  end="")
            time.sleep(0.5)
        print()
