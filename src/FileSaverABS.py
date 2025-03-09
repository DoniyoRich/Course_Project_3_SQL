from abc import ABC, abstractmethod


class FileSaver(ABC):

    @abstractmethod
    def save_to_file(self, vacancy: list[tuple], columns: list[str], filename='') -> None:
        """ Абстрактный метод сохранения списка словарей в файл. """
        pass
