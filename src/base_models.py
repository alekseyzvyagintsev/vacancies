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
