########################################################################
import abc


class JobAPI(abc.ABC):
    @abc.abstractmethod
    def _connect(self):
        """
        Метод подключения к API
        """
        pass

    @abc.abstractmethod
    def get_vacancies(self, keyword: str, amount: int) -> list:
        """
        Метод получения вакансий по ключевому слову
        """
        pass


class AbstractFileStorage:
    @abc.abstractmethod
    def add_vacancy(self, vacancy):
        # Добавляет вакансию в файл
        pass

    @abc.abstractmethod
    def delete_vacancy(self, vacancy_id):
        # Удаляет указанную вакансию
        pass


class DBInteraction(abc.ABC):
    @abc.abstractmethod
    def create_db(self) -> None:
        """
        Метод для создания базы данных
        """
        pass

    @abc.abstractmethod
    def create_tables(self) -> None:
        """
        Метод для создания таблицы
        """
        pass

    @abc.abstractmethod
    def read_table(self):
        """
        Метод для чтения таблицы
        """
        pass

    @abc.abstractmethod
    def update_table(self):
        """
        Метод для обновления таблицы
        """
        pass

    @abc.abstractmethod
    def clearing_table(self):
        """
        Метод для очистки таблицы
        """
        pass


########################################################################
