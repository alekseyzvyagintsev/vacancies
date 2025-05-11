
import requests


class HeadHunterAPI:
    BASE_URL = 'http://api.hh.ru/vacancies'

    def __init__(self):
        self.__session = None

    def _connect(self):
        """
        Метод подключения к API
        """
        self.__session = requests.Session()
        response = self.__session.get(self.BASE_URL)
        response.raise_for_status()
        return response


    def load_vacancies(self, keyword):
        """
        Метод получения вакансий по ключевому слову
        """
        self._connect()
        params = {
            'text': keyword,
            'per_page': 100,
            'page': 2
        }

        response = self.__session.get(self.BASE_URL, params=params)
        vacancies = response.json().get('items', [])

        only_with_salary = True

        return [
            {
                'name': vacancie.get('name'),
                'salary': f"{vacancie.get('salary', {}).get('from')} - {vacancie.get('salary', {}).get('to')}",
                'url': vacancie.get('url'),
                'description': vacancie.get('snippet', {}).get('responsibility'),
                'city': vacancie.get('area').get('name')
            }
            for vacancie in vacancies
            if (vacancie.get('salary') is not None and (
                        vacancie.get('salary', {}).get('from') is not None or vacancie.get('salary', {}).get(
                    'to') is not None))
        ]



if __name__ == '__main__':
    hh_api = HeadHunterAPI()

    try:
        vacancies = hh_api.load_vacancies("Python")
        print(vacancies)
    except Exception as e:
        print(f'Произошла ошибка: {e}')