import pandas as pd

from src.FileSaverABS import FileSaver


class ExcelSaver(FileSaver):
    """ Класс работы с файлами Excel. Реализован метод сохранения списка вакансий в файл. """

    def save_to_file(self, vacancies: list[dict], filename: str = 'vacancies') -> None:
        """
        Метод преобразует полученный список вакансий в датафрейм pandas
        и сохраняет в файл формата EXCEL.
        """
        print("Записываю в файл EXCEL, возможно придется немного подождать...")
        df = pd.DataFrame(vacancies)
        df.to_excel(filename + '.xlsx', index=False)
