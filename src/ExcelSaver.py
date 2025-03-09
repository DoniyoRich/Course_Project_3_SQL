import logging

import pandas as pd

from src.constants import DATA_DIR
from src.FileSaverABS import FileSaver


class ExcelSaver(FileSaver):
    """ Класс работы с файлами Excel. Реализован метод сохранения списка вакансий в файл. """

    def save_to_file(self, vacancies: list[tuple], columns: list[str], filename: str = 'vacancies') -> None:
        """
        Метод преобразует полученный список вакансий в датафрейм pandas
        и сохраняет в файл формата EXCEL.
        """
        print("Записываю в файл EXCEL, возможно придется немного подождать...")
        df = pd.DataFrame(vacancies, columns=columns)
        try:
            df.to_excel(DATA_DIR + filename + '.xlsx', index=False)
            print(f"Файл {filename}.xlsx успешно записан в папку /data.")
            logging.info(f"Файл {filename}.xlsx успешно записан в папку /data.")
        except Exception as e:
            print(f'Произошла ошибка при записи файла: {e}')
            logging.error(f'Произошла ошибка при записи файла: {e}')
