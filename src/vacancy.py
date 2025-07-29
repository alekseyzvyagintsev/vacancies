############################################################################################
import re

from src.logging_vacancy import logger


class Vacancy:
    __slots__ = ["name", "salary", "_url", "description", "city"]

    def __init__(self, name, salary, url, description, city) -> None:
        self._validate_attributes(name, salary, url, description, city)
        self.name = name
        self.salary = salary
        self._url = url
        self.description = description
        self.city = city

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, value):
        # Допустима любая дополнительная валидация
        self._url = value

    def _validate_attributes(self, name, salary, url, description, city):
        """Приватный метод для проверки правильности значений атрибутов"""
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Имя вакансии должно быть непустым текстом.")
        if not isinstance(url, str) or not url.startswith(("http://", "https://")):
            raise ValueError("URL должен начинаться с http:// или https://.")
        if not isinstance(description, str) or not description.strip():
            raise ValueError("Описание должно быть непустым текстом.")
        if not isinstance(city, str) or not city.strip():
            raise ValueError("Город должен быть непустым текстом.")

    def __repr__(self) -> str:
        """Метод выводит информацию о вакансии в порядке инициализации объекта"""
        return f"{self.name}, {self.salary}, {self.url}, {self.description}, {self.city}"

    def __str__(self) -> str:
        """Метод выводит информацию о вакансии в отформатированном виде"""
        return f"{self.city}, {self.name}, {self.salary}, {self.url}, {self.description}"

    def __lt__(self, other):
        return self.average_salary() < other.average_salary()

    def __gt__(self, other):
        return self.average_salary() > other.average_salary()

    def __eq__(self, other):
        return self.average_salary() == other.average_salary()

    def average_salary(self):
        """Вычисляем среднее значение зарплаты одной вакансии"""
        # Проверяем корректность строки с зарплатой
        if self.salary is None or self.salary == "" or "none" in self.salary.lower():
            return 0  # Если зарплата не указана или не распознана, возвращаем 0
        # Парсим зарплату и считаем среднее значение
        elif "-" in self.salary:
            parts = self.salary.split("-")
            # Очистка обеих частей от лишних символов (валюта, точки и пробелы)
            cleaned_parts = [re.sub(r"\D", "", part) for part in parts]
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
            "name": self.name,
            "salary": self.salary,
            "url": self.url,
            "description": self.description,
            "city": self.city,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


############################################################################################
