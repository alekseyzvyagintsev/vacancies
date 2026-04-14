#########################################################################################################
import requests

from src.base_models import JobAPI
from src.logging_api import logger


class HeadHunterAPI(JobAPI):
    BASE_URL = "http://api.hh.ru/vacancies"

    def __init__(self) -> None:
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
            logger.error(f"response.status_code != 200: {response.status_code}")
        response.raise_for_status()
        return response

    def get_vacancies(self, keyword: str = None, amount: int = None, url: str = None) -> list:
        """
        Метод получения вакансий по ключевому слову
        """
        # Запускаем сессию
        self._connect()

        if not url:
            if keyword is None:
                keyword = ""
            if amount is None:
                amount = 100
            # Создаем параметры для запроса
            params = {
                "text": keyword,
                "per_page": amount,
                "page": 1,
            }
            # Получаем данные по запросу
            response = self.__session.get(self.BASE_URL, params=params)
            if response.status_code != 200:
                logger.error(f"Ошибка подключения к API {response.status_code}")
                raise Exception(f"Ошибка подключения к API {response.status_code}")

            logger.info(f"Успех. Данные с портала {self.BASE_URL} получены")
        else:
            # Получаем данные по запросу
            self.BASE_URL = url
            response = self.__session.get(self.BASE_URL)
            if response.status_code != 200:
                logger.error(f"Ошибка подключения к API {response.status_code}")
                raise Exception(f"Ошибка подключения к API {response.status_code}")

            logger.info(f"Успех. Данные с портала {keyword} получены")
        # Возвращаем данные хранящиеся по ключу 'items' или пустой список если нет такого ключа
        # print(response.json().get("items", []))
        return response.json().get("items", [])


#########################################################################################################
