############################################################################################
import json
import os
from typing import List, Union, Any

from src.base_models import AbstractFileStorage
from src.hh_api_interaction import HeadHunterAPI
from src.iterator import VacanciesIterator
from src.vacancy import Vacancy
from src.logging_vacancies import logger


class JSONSaver(AbstractFileStorage):

    def __init__(self, file_name: str='vacancies') -> None:
        self.__file_name = os.path.join(os.path.dirname(os.path.dirname(__file__)), f'data/{file_name}.json')

    @property
    def get_file_path(self) -> str:
        return self.__file_name

    def load_vacancies(self) -> list[Vacancy] | list:
        """
        Загружает данные из файла в переменную в режиме чтения,
        возвращает список словарей
        """
        with open(self.get_file_path, 'r') as file:
            try:
                data = json.load(file)
                data_from_file = data.get('vacancies', [])
                iterator = VacanciesIterator(data_from_file)
                return [Vacancy.from_dict(v) for v in iterator]
            except json.JSONDecodeError:
                self.save_vacancies([])
                return []

    def add_vacancy(self, value: Vacancy | list[Vacancy]) -> None:
        """
        Добавляет вакансию в конец файла.
        Читает файл в переменную,
        Если передается одиночная вакансия — добавляет её,
        если список вакансий — добавляет весь список.
        """
        if not value:
            logger.error(f'Нет данных для добавления: {type(value)} - {value}')
            return
        vac_from_file = self.load_vacancies()
        # Проверяем новые вакансии на уникальность
        unique_vac = self.find_unique_vacancies(vac_from_file, value)
        if isinstance(unique_vac, list) and len(unique_vac) > 0 and all(isinstance(v, Vacancy) for v in unique_vac):
            logger.info(f'Добавляется список вакансий: {type(unique_vac[-1])} - {unique_vac[-1]}')
            vac_from_file.extend(unique_vac)
        elif not unique_vac:
            logger.info(f'Нет уникальных вакансий для добавления: {type(value)} - {value}')
            return
        else:
            logger.error(f'Неверный формат данных: {type(value)} - {value}')
        # Сохраняем
        if vac_from_file:
            logger.info(f'Исходящие данные для сохранения:{type(vac_from_file[-1])} - {vac_from_file[-1]}')
            self.save_list_vacancies(list(vac_from_file))
        else:
            logger.error(f'Для сохранения нечего передавать?!!!: {type(vac_from_file[-1])} - {vac_from_file[-1]}')

    def save_vacancies(self, json_vacancies: list[dict[str, str]]) -> None:
        """ Перезаписывает файл входящими json-данными (списка словарей) """
        with open(self.get_file_path, 'w', encoding='utf-8') as file:
            json.dump({'vacancies': json_vacancies}, file, ensure_ascii=False, indent=4)

    def save_list_vacancies(self, list_vacancies: list | list[Vacancy]) -> None:
        """ Перезаписывает файл входящим списком вакансий """
        if not list_vacancies or len(list_vacancies) == 0:
            logger.info(f'Передан пустой список, действие отменено {type(list_vacancies)} - {list_vacancies}')
            return
        if isinstance(list_vacancies[0], Vacancy):
            if list_vacancies:
                logger.info(f'Вошёл список объектов Vacancy: {type(list_vacancies[-1])} - {list_vacancies[-1]}')
            logger.info('Сериализуем объекты вакансий в список словарей')
            serialized_data = [vacancy.to_dict() for vacancy in list_vacancies]
        else:
            if list_vacancies:
                logger.info(f'Вошёл список словарей: {type(list_vacancies[-1])} - {list_vacancies[-1]}')
            serialized_data = list_vacancies
        logger.info('Перезаписываем файл данными')
        with open(self.get_file_path, 'w', encoding='utf-8') as file:
            json.dump({'vacancies': serialized_data}, file, ensure_ascii=False, indent=4)

    def delete_vacancy(self, value: Vacancy | str) -> None:
        """ Удаляет из файла по входящему названию """
        global updated_vacancies
        vacancies = self.load_vacancies()
        logger.info('Проверяем формат данных и выполняем удаление соответственно')
        if isinstance(vacancies[0], Vacancy):
            updated_vacancies = [v for v in vacancies if v != value]
        elif isinstance(vacancies, list):
            logger.info('Проверяем типы элементов списка')
            if all(isinstance(v, dict) for v in vacancies):
                logger.info('Формат данных: список словарей фильтруем список вакансий по ключу имя')
                updated_vacancies = [v for v in vacancies if v.name != value]
            elif all(isinstance(v, str) for v in vacancies):
                logger.info('Формат данных: список строк фильтруем список вакансий сравнивая строки')
                updated_vacancies = [v for v in vacancies if value not in v]
            else:
                logger.error('Смешанный формат или неизвестный тип данных')
                raise ValueError("Недопустимый формат данных вакансий")
        else:
            logger.error("Получены недопустимые данные, ожидался список")
            raise ValueError("Получены недопустимые данные, ожидался список")
        if updated_vacancies:
            self.save_list_vacancies(updated_vacancies)
        else:
            self.save_vacancies([])
            logger.info('Список пуст, был удален последний элемент, файл перезаписан пустым списком')

    @staticmethod
    def find_unique_vacancies(existing_vacancies: List[Vacancy], new_vacancies: Union[List[Vacancy], Vacancy]) -> List[
        Vacancy]:
        """
        Сравнивает списки и возвращает из второго списка список уникальных вакансий.
        """
        if isinstance(new_vacancies, Vacancy):
            logger.info(f'Пришёл одиночный объект для сравнения {new_vacancies}')
            new_vacancies = [new_vacancies]
        if not existing_vacancies:
            logger.error('Если эталонный список пуст возвращаем список новых вакансий без изменения')
            return new_vacancies
        if not new_vacancies:
            logger.error(f'Пришёл пустой список для сравнения {new_vacancies}')
            return []
        logger.info('Получаем подписи всех существующих вакансий')
        signatures_from_existing_vacancies = {
            f"{v.name}-{v.url}"
            for v in existing_vacancies
        }
        logger.info('Фильтруем новые вакансии, оставляя только уникальные')
        unique_vacancies = [
            v for v in new_vacancies
            if f"{v.name}-{v.url}" not in signatures_from_existing_vacancies
        ]
        return unique_vacancies

    @staticmethod
    def is_list_vacancies(value: Any) -> bool:
        """ Проверяем, что передан именно список вакансий """
        if not isinstance(value, list) or not all(isinstance(item, Vacancy) for item in value):
            return False
        else:
            return True

    @staticmethod
    def cast_to_object_list(json_data: list[dict[str, str]]) -> list[Vacancy]:
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
    def filter_by_criteria(criteria: str | list, vacancies_list=None) -> list[Vacancy]:
        """
        Фильтрует данные на 'лету' по входящему критерию,
        либо предварительно загрузив из файла.
        Поиск ведется по всей доступной информации о вакансии.
        """
        # Если критерии пусты, возвращаем весь список
        if not criteria:
            if vacancies_list is None:
                return JSONSaver().load_vacancies()
            return vacancies_list

        # Нормализуем критерии поиска (приведение к нижнему регистру)
        if isinstance(criteria, str) and len(criteria) > 0:
            normalized_criteria = criteria.strip().lower()
        elif isinstance(criteria, list) and len(criteria) > 0:
            normalized_criteria = [c.strip().lower() for c in criteria]
        else:
            raise TypeError("Критерии должны быть либо строкой, либо списком")

        result = []

        # Если источник вакансий не указан, берем данные из файла
        if not vacancies_list:
            vacancies = JSONSaver().load_vacancies()
        else:
            vacancies = vacancies_list

        # Используем метод __str__, чтобы легко искать по всей информации о вакансии
        for vacancy in vacancies:
            vacancy_str = str(vacancy).strip().lower()

            # Проверяем соответствие критерию
            if isinstance(normalized_criteria, str):
                if normalized_criteria in vacancy_str:
                    result.append(vacancy)
                    print(f"Crit: {normalized_criteria}\nVacancy Str: {vacancy_str}")
            elif isinstance(normalized_criteria, list):
                if any(word in vacancy_str for word in normalized_criteria):
                    result.append(vacancy)
                    print(f"Crit: {normalized_criteria}\nVacancy Str: {vacancy_str}")

        return result

    @staticmethod
    def sort_vacancies(vacancies: list[Vacancy]) -> list[Vacancy]:
        """Сортируем вакансии по убыванию среднего уровня зарплаты"""
        return sorted(vacancies, key=lambda v: v.average_salary(), reverse=True)

    @staticmethod
    def get_top_vacancies(sorted_vacancies: list[Vacancy], top_n: int) -> list[Vacancy]:
        """Берём первые top_n вакансий из отсортированных"""
        return sorted_vacancies[:min(len(sorted_vacancies), top_n)]

    @staticmethod
    def get_vacancies_in_salary_range(vacancies: list[Vacancy], salary_range: str) -> list[Vacancy]:
        """ Фильтрует по признаку зарплата в указанном диапазоне """
        # Проверяем что на вход пришли данные.
        if not salary_range:
            return [v for v in vacancies if v.average_salary() is not None]
        # Преобразуем границы диапазона в числа.
        min_salary, max_salary = map(float, salary_range.split('-'))
        # Отбираем вакансии, попадающие в указанный диапазон зарплат
        return [
            v for v in vacancies if v.average_salary() is not None and min_salary <= v.average_salary() <= max_salary
        ]

    @staticmethod
    def print_vacancies(list_vacancies: list) -> None:
        """Выводим полученный список построчно"""
        if isinstance(list_vacancies, list):
            for vacancy in list_vacancies:
                print(vacancy)


if __name__ == '__main__':
    # hh_api = HeadHunterAPI()
    # vacancies = ''
    # list_vacancies = []
    # try:
    #     vacancies = hh_api.get_vacancies("Python", 10)
    # except Exception as e:
    #     print(f'Произошла ошибка: {e}')
    #
    # print(vacancies)
    # print('1' * 100)
    #
    # try:
    #     list_vacancies = JSONSaver.cast_to_object_list(vacancies)
    # except Exception as e:
    #     print(f'Произошла ошибка: {e}')
    #
    # iterator = VacanciesIterator(list_vacancies)
    # print(next(iterator))
    # print(list_vacancies)
    # print('2' * 100)
    #
    # vacancie = Vacancy(
    #     "Python Developer",
    #     "100000-150000 руб.",
    #     "<https://hh.ru/vacancy/123456>",
    #     "Требования: опыт работы от 3 лет...",
    #     "Москва",
    # )
    # json_saver = JSONSaver()
    # json_saver.save_vacancies(vacancies)
    # json_saver.save_list_vacancies(list_vacancies)
    # print(json_saver.load_vacancies())
    # json_saver.add_vacancy(vacancie)
    # json_saver.delete_vacancy('Junior Devops')

    # Пример создания вакансий
    vacancy1 = Vacancy("Python-разработчик", "70000-100000", "https://hh.ru/vacancy/1",
                       "Требуется опыт разработки на Python", "Москва")
    vacancy2 = Vacancy("Frontend-разработчик", "80000-120000", "https://hh.ru/vacancy/2", "Требуются знания React.js",
                       "Санкт-Петербург")

    # Добавляем вакансии в хранилище
    json_saver = JSONSaver()
    # json_saver.save_vacancies([vacancy1.__dict__, vacancy2.__dict__])
    #
    # # Поиск вакансий в диапазоне зарплат
    # result = json_saver.get_vacancies_in_salary_range(75000, 110000)
    # for vacancy in result:
    #     print(vacancy)

    json_saver.save_vacancies([])
    json_saver.add_vacancy([vacancy1, vacancy2])

    filtered_vacancies = json_saver.filter_by_criteria('Санкт-Петербург')

    print(filtered_vacancies)


############################################################################################
