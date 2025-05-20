import re

from src.hh_api_interaction import HeadHunterAPI
from src.logging_vacancy import logger


class Vacancy():

    def __init__(self, name, salary, url, description, city) -> None:
        self.name = name
        self.salary = salary
        self.url = url
        self.description = description
        self.city = city

    def __repr__(self) -> str:
        """Метод выводит информацию о вакансии в порядке инициализации объекта"""
        return f'{self.name}, {self.salary}, {self.url}, {self.description}, {self.city}'

    def __str__(self) -> str:
        """Метод выводит информацию о вакансии в отформатированном виде"""
        return f'{self.city}, {self.name}, {self.salary}, {self.url}, {self.description}'

    def __lt__(self, other):
        return self.average_salary() < other.average_salary()

    def __gt__(self, other):
        return self.average_salary() > other.average_salary()

    def __eq__(self, other):
        return self.average_salary() == other.average_salary()

    def average_salary(self):
        # Проверяем корректность строки с зарплатой
        if self.salary is None or self.salary == "" or "none" in self.salary.lower():
            return 0  # Если зарплата не указана или не распознана, возвращаем 0
        # Парсим зарплату и считаем среднее значение
        elif "-" in self.salary:
            parts = self.salary.split('-')
            # Очистка обеих частей от лишних символов (валюта, точки и пробелы)
            cleaned_parts = [re.sub(r'\D', '', part) for part in parts]
            try:
                low, high = map(float, cleaned_parts)
                return (low + high) / 2
            except Exception as e:
                logger.error(f"Не удалось разобрать salary '{self.salary}' из-за ошибки: {e}")
                return 0
        elif self.salary.isdigit():  # Если зарплата указана одним числом
            return float(self.salary)

    def to_dict(self):
        return {
            'name': self.name,
            'salary': self.salary,
            'url': self.url,
            'description': self.description,
            'city': self.city
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


if __name__ == '__main__':
    hh_api = HeadHunterAPI()
    vacancies = ''
    try:
        vacancies = hh_api.get_vacancies("Python")
        # print(vacancies)
        # print('1' * 100)
    except Exception as e:
        print(f'Произошла ошибка: {e}')

