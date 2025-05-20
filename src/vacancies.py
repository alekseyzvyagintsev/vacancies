import json
import os
from src.base_models import AbstractFileStorage
from src.hh_api_interaction import HeadHunterAPI
from src.iterator import VacancieIterator
from src.vacancy import Vacancy
from src.logging_vacancies import logger


class JSONSaver(AbstractFileStorage):

    def __init__(self, file_name: str='data/vacancies.json'):
        self.__file_name = os.path.join(os.path.dirname(os.path.dirname(__file__)), file_name)

    def load_vacancies(self) -> list:
        """
        Загружает данные из файла в переменную в режиме чтения,
        возвращает список словарей
        """
        with open(self.__file_name, 'r') as file:
            try:
                data = json.load(file)
                data_from_file = data.get('vacancies', [])
                iterator = VacancieIterator(data_from_file)
                return [Vacancy.from_dict(v) for v in iterator]
            except json.JSONDecodeError:
                return []

    def add_vacancy(self, value):
        """
        Добавляет вакансию в конец файла.
        Читает файл в переменную,
        добавляет элемент в конец списка,
        перезаписывает старый файл с новыми данными
        """
        vacancies = self.load_vacancies()
        logger.info(f'Последняя вакансия в файле: its type {type(vacancies[-1])} - {vacancies[-1]}')
        # Если передана на вход одна вакансия
        if isinstance(value, Vacancy):
            logger.info(f'Вошла одна вакансия: its type {type(value)} - {value}')
            # Добавляем одну вакансию
            try:
                vacancies.append(value)
            except ValueError as e:
                logger.error(e)
        # Проверяем, что передан именно список вакансий
        elif self.is_list_vacancies(value):
            logger.info(f'Вошёл список объектов Vacancy: its type {type(value[-1])} - {value[-1]}')
            for v in value:
                vacancies.append(v)
        # Сохраняем
        logger.info(f'Исходящие данные для сохранения: its type {type(vacancies[-1])} - {vacancies[-1]}')
        self.save_list_vacancies(list(vacancies))

    def save_vacancies(self, json_vacancies):
        """ Перезаписывает файл входящими json-данными """
        with open(self.__file_name, 'w', encoding='utf-8') as file:
            json.dump({'vacancies': json_vacancies}, file, ensure_ascii=False, indent=4)

    def save_list_vacancies(self, list_vacancies):
        """ Перезаписывает файл входящим списком вакансий """

        # Проверяем, что передан именно список объектов вакансий
        if isinstance(list_vacancies[0], Vacancy):
            logger.info(f'Вошёл список объектов Vacancy: its type {type(list_vacancies[-1])} - {list_vacancies[-1]}')
            # Сериализуем объекты вакансий в список словарей
            serialized_data = [vacancy.to_dict() for vacancy in list_vacancies]
        else:
            logger.info(f'Вошёл список словарей: its type {type(list_vacancies[-1])} - {list_vacancies[-1]}')
            serialized_data = list_vacancies
        # Перезаписываем файл данными
        with open(self.__file_name, 'w', encoding='utf-8') as file:
            json.dump({'vacancies': serialized_data}, file, ensure_ascii=False, indent=4)

    def delete_vacancy(self, value):
        """ Удаляет из файла по входящему названию """
        global updated_vacancies
        vacancies = self.load_vacancies()
        # Проверяем формат данных и выполняем удаление соответственно
        if isinstance(vacancies[0], Vacancy):
            updated_vacancies = [v for v in vacancies if v != value]
        elif isinstance(vacancies, list):
            # Проверяем типы элементов списка
            if all(isinstance(v, dict) for v in vacancies):
                # Формат данных: список словарей
                updated_vacancies = [v for v in vacancies if v.get('name') != value]
            elif all(isinstance(v, str) for v in vacancies):
                # Формат данных: список строк
                updated_vacancies = [v for v in vacancies if value not in v]
            else:
                # Смешанный формат или неизвестный тип данных
                raise ValueError("Недопустимый формат данных вакансий")
        else:
            raise ValueError("Получены недопустимые данные, ожидался список")
        self.save_list_vacancies(updated_vacancies)

    @staticmethod
    def is_list_vacancies(list_vacancies):
        """ Проверяем, что передан именно список вакансий """
        if not isinstance(list_vacancies, list) or not all(isinstance(item, Vacancy) for item in list_vacancies):
            return False
        else:
            return True

    @staticmethod
    def cast_to_object_list(json_data):
        """
        Создает объекты вакансий из входящих json-данных
        и собирает в список
        """
        result = []
        for item in json_data:
            if (item.get('salary') is not None and (
                    item.get('salary', {}).get('from') is not None or item.get('salary', {}).get('to') is not None)):
                salary = (f""
                          f"{item.get('salary', {}).get('from')}-"
                          f"{item.get('salary', {}).get('to')} "
                          f"{item.get('salary', {}).get('currency')}.")
            else:
                salary = "Зарплата не указана"

            result.append(Vacancy(
                name=item.get('name'),
                salary=salary,
                url=item.get('alternate_url'),
                description=item.get('snippet', {}).get('requirement'),
                city=item.get('area', {}).get('name')
            ))
        return result

    @staticmethod
    def filter_by_criteria(criteria, vacancies_list=None):
        """
        Фильтрует данные на 'лету' по входящему критерию,
        либо предварительно загрузив из файла.
        Поиск ведется по всему объекту вакансии.
        """
        # Нормализуем разные варианты критерия для фильтрации
        if isinstance(criteria, str):
            normalized_criteria = criteria.strip().lower()
        elif isinstance(criteria, list):
            normalized_criteria = [c.strip().lower() for c in criteria]
        else:
            raise TypeError("Критерии должны быть либо строкой, либо списком")

        result = []

        # Проверяем объект фильтрации
        if not vacancies_list:
            vacancies = JSONSaver().load_vacancies()
            if vacancies:
                for vacancy in vacancies:
                    fields_to_check = [getattr(vacancy, attr) for attr in ['name', 'salary', 'city', 'description'] if
                                       hasattr(vacancy, attr)]
                    # Определяемся с условием фильтрации
                    if isinstance(normalized_criteria, str):
                        # Одинокий критерий
                        if any(normalized_criteria in field.lower() for field in fields_to_check if
                               isinstance(field, str)):
                            result.append(vacancy)
                    elif isinstance(normalized_criteria, list):
                        # Несколько критериев
                        if any(any(word in field.lower() for word in normalized_criteria) for field in fields_to_check
                               if isinstance(field, str)):
                            result.append(vacancy)
            return result
        else:
            for vacancy in vacancies_list:
                fields_to_check = [getattr(vacancy, attr) for attr in ['name', 'salary', 'city', 'description'] if
                                   hasattr(vacancy, attr)]
                # Определяемся с условием фильтрации
                if isinstance(normalized_criteria, str):
                    # Одинокий критерий
                    if any(normalized_criteria in field.lower() for field in fields_to_check if
                           isinstance(field, str)):
                        result.append(vacancy)
                elif isinstance(normalized_criteria, list):
                    # Несколько критериев
                    if any(any(word in field.lower() for word in normalized_criteria) for field in fields_to_check
                           if isinstance(field, str)):
                        result.append(vacancy)
            return result

    @staticmethod
    def sort_vacancies(vacancies):
        # Сортируем вакансии по средней зарплате
        return sorted(vacancies, key=lambda v: v.average_salary(), reverse=True)

    @staticmethod
    def get_top_vacancies(sorted_vacancies, top_n):
        # Берём первые top_n вакансий из отсортированных
        return sorted_vacancies[:min(len(sorted_vacancies), top_n)]

    @staticmethod
    def get_vacancies_in_salary_range(vacancies, salary_range):
        """ Фильтрует по признаку зарплата в указанном диапазоне """
        # Преобразуем границы диапазона в числа
        min_salary, max_salary = map(float, salary_range.split('-'))
        # Отбираем вакансии, попадающие в указанный диапазон зарплат
        return [
            v for v in vacancies if v.average_salary() is not None and min_salary <= v.average_salary() <= max_salary
        ]

    @staticmethod
    def print_vacancies(list_vacancies):
        # Выводим полученный список построчно
        if isinstance(list_vacancies, list):
            for vacancy in list_vacancies:
                print(vacancy)


if __name__ == '__main__':
    hh_api = HeadHunterAPI()
    vacancies = ''
    list_vacancies = []
    try:
        vacancies = hh_api.get_vacancies("Python", 10)
    except Exception as e:
        print(f'Произошла ошибка: {e}')

    # print(vacancies)
    print('1' * 100)

    try:
        list_vacancies = JSONSaver.cast_to_object_list(vacancies)
    except Exception as e:
        print(f'Произошла ошибка: {e}')

    # iterator = VacancieIterator(list_vacancies)
    # print(next(iterator))
    # print(list_vacancies)
    print('2' * 100)

    # vacancie = Vacancy(
    #     "Python Developer",
    #     "100000-150000 руб.",
    #     "<https://hh.ru/vacancy/123456>",
    #     "Требования: опыт работы от 3 лет...",
    #     "Москва",
    # )
    json_saver = JSONSaver()
    # json_saver.save_vacancies(vacancies)
    json_saver.save_list_vacancies(list_vacancies)
    print(json_saver.load_vacancies())
    # json_saver.add_vacancy(vacancie)
    # json_saver.delete_vacancy('Junior Devops')
    #
    # # Пример создания вакансий
    # vacancy1 = Vacancy("Python-разработчик", "70000-100000", "https://hh.ru/vacancy/1",
    #                    "Требуется опыт разработки на Python", "Москва")
    # vacancy2 = Vacancy("Frontend-разработчик", "80000-120000", "https://hh.ru/vacancy/2", "Требуются знания React.js",
    #                    "Санкт-Петербург")
    #
    # # Добавляем вакансии в хранилище
    # json_saver = JSONSaver()
    # json_saver.save_vacancies([vacancy1.__dict__, vacancy2.__dict__])
    #
    # # Поиск вакансий в диапазоне зарплат
    # result = json_saver.get_vacancies_in_salary_range(75000, 110000)
    # for vacancy in result:
    #     print(vacancy)