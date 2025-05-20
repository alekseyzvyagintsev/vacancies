# from src.vacancies import JSONSaver
# from src.vacancy import Vacancy
#
#
# class VacancyMixin:
#
#     @staticmethod
#     def is_list_vacancies(list_vacancies):
#         """ Проверяем, что передан именно список вакансий """
#         if not isinstance(list_vacancies, list) or not all(isinstance(item, Vacancy) for item in list_vacancies):
#             return False
#         else:
#             return True
#
#     @staticmethod
#     def cast_to_object_list(json_data):
#         """
#         Создает объекты вакансий из входящих json-данных
#         и собирает в список
#         """
#         result = []
#         for item in json_data:
#             if (item.get('salary') is not None and (
#                     item.get('salary', {}).get('from') is not None or item.get('salary', {}).get('to') is not None)):
#                 salary = (f""
#                           f"{item.get('salary', {}).get('from')}-"
#                           f"{item.get('salary', {}).get('to')} "
#                           f"{item.get('salary', {}).get('currency')}.")
#             else:
#                 salary = "Зарплата не указана"
#
#             result.append(Vacancy(
#                 name=item.get('name'),
#                 salary=salary,
#                 url=item.get('alternate_url'),
#                 description=item.get('snippet', {}).get('requirement'),
#                 city=item.get('area', {}).get('name')
#             ))
#         return result
#
#     @staticmethod
#     def filter_by_criteria(criteria, vacancies_list=None):
#         """
#         Фильтрует данные на 'лету' по входящему критерию,
#         либо предварительно загрузив из файла.
#         Поиск ведется по всему объекту вакансии.
#         """
#         if not vacancies_list:
#             json_saver = JSONSaver()
#             vacancies = json_saver.load_vacancies()
#             normalized_criteria = criteria.strip().lower()
#             result = []
#             if vacancies:
#                 for vacancy in vacancies:
#                     # Перебираем все доступные поля объекта
#                     fields_to_check = [getattr(vacancy, attr) for attr in ['name', 'salary', 'city', 'description']]
#                     # Проверяем наличие критерия в одном из полей
#                     if any(normalized_criteria in field.lower() for field in fields_to_check if isinstance(field, str)):
#                         result.append(vacancy)
#             return result
#         else:
#             vacancies = vacancies_list
#             normalized_criteria = criteria.strip().lower()
#             result = []
#             if vacancies:
#                 for vacancy in vacancies:
#                     # Перебираем все доступные поля объекта
#                     fields_to_check = [getattr(vacancy, attr) for attr in ['name', 'salary', 'city', 'description']]
#                     # Проверяем наличие критерия в одном из полей
#                     if any(normalized_criteria in field.lower() for field in fields_to_check if isinstance(field, str)):
#                         result.append(vacancy)
#             return result
#
#     @staticmethod
#     def sort_vacancies(vacancies):
#         # Сортируем вакансии по средней зарплате
#         return sorted(vacancies, key=lambda v: v.average_salary(), reverse=True)
#
#     @staticmethod
#     def get_top_vacancies(sorted_vacancies, top_n):
#         # Берём первые top_n вакансий из отсортированных
#         return sorted_vacancies[:min(len(sorted_vacancies), top_n)]
#
#     @staticmethod
#     def get_vacancies_in_salary_range(vacancies, salary_range):
#         """ Фильтрует по признаку зарплата в указанном диапазоне """
#         # Преобразуем границы диапазона в числа
#         min_salary, max_salary = map(float, salary_range.split())
#         # Отбираем вакансии, попадающие в указанный диапазон зарплат
#         return [v for v in vacancies if min_salary <= v.average_salary() <= max_salary]
#
#     @staticmethod
#     def print_vacancies(list_vacancies):
#         # Выводим полученный список построчно
#         if isinstance(list_vacancies, list):
#             for vacancy in list_vacancies:
#                 print(vacancy)