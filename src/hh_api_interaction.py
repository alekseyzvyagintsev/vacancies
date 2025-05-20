#########################################################################################################
import requests

from src.logging_api import logger
from src.base_models import JobAPI


class HeadHunterAPI(JobAPI):
    BASE_URL = 'http://api.hh.ru/vacancies'

    def __init__(self):
        self.__session = None

    def _connect(self):
        """
        Метод подключения к API
        """
        timeout = 10  # секунд
        # Создание HTTP сессии
        self.__session = requests.Session()
        # Отправка GET-запроса
        response = self.__session.get(self.BASE_URL, timeout=timeout)
        # Проверка статуса ответа
        if response.status_code != 200:
            logger.error(f'response.status_code != 200: {response.status_code}')
        response.raise_for_status()
        return response


    def get_vacancies(self, keyword: str, amount: int=None) -> list:
        """
        Метод получения вакансий по ключевому слову
        """
        if not keyword:
            logger.error('Провал. Необходимо указать наименование вакансии')
            raise ValueError('Необходимо указать наименование вакансии')
        if amount is None:
            amount = 100
        self._connect()
        params = {
            'text': keyword,
            'per_page': amount,
            'page': 1,
        }

        response = self.__session.get(self.BASE_URL, params=params)
        if response.status_code != 200:
            logger.error(f'Ошибка подключения к API {response.status_code}')
            raise Exception(f'Ошибка подключения к API {response.status_code}')

        logger.info(f'Успех. Данные с портала {self.BASE_URL} получены')
        return response.json().get('items', [])



# if __name__ == '__main__':
#     hh_api = HeadHunterAPI()
#
#     try:
#         vacancies = hh_api.get_vacancies('Python', 1)
#         print(vacancies)
#     except Exception as e:
#         print(f'Произошла ошибка: {e}')

#########################################################################################################