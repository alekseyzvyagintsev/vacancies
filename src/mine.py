#######################################################################################################
from requests import HTTPError

from src.logging_main import logger
from src.hh_api_interaction import HeadHunterAPI
from src.vacancies import JSONSaver
from src.vacancy import Vacancy


def user_job_request():
    """ Диалог с пользователем для получения вакансий по API"""

    # Выбор Сайта для запроса или отказ и выход из программы
    global hh_api
    print("\nДля получения вакансий сделайте выбор.")
    print("1. Поиск вакансий на hh.ru")
    print("0. Выход из программы.")

    try:
        user_choice = int(input("Введите свой выбор: "))
    except ValueError:
        print('Введите номер списка меню.')
        logger.info('Не веден номер списка меню.')
        return None

    if user_choice == 0:
        print('Программа закрыта.')
        logger.info('Программа закрыта.')
        return 0
    elif user_choice != 1 and user_choice != 2:
        print('Допустимы числа от 0 до 2')
        logger.info("Введены недопустимые числа")
        return None

    # Переменную количество объявлений делаем необязательной
    try:
        amount = int(input('Сколько вакансий получить на сайте (не обязательно)?: '))
    except ValueError:
        logger.info('Принимаются только числа. Введенная строка игнорируется')
        amount = None

    keyword = input('Введите поисковый запрос (например: Python разработчик): ')

    try:
        hh_api = HeadHunterAPI()
    except HTTPError as e:
        logger.error(e)
    try:
        vacancies = hh_api.get_vacancies(keyword, amount)
        return vacancies
    except Exception as e:
        logger.error(f'Произошла ошибка: {e}')
        return None


def sort_by_city(vacancies_list, city=None):
    """ Фильтрует данные по запрошенному названию города """
    if city is None:
        return vacancies_list
    else:
        jason_saver = JSONSaver()
        try:
            city_vacancies = jason_saver.filter_by_criteria(city, vacancies_list)
            return city_vacancies
        except ValueError as e:
            logger.error(f'{__name__}: "Фильтрация данных провалилась" ({e})')
        except TypeError as e:
            logger.error(f'{__name__}: "Фильтрация данных провалилась" ({e})')

def adding_new_vacancies_to_file(vacancies_list):
    """ проверяет отсутствие вакансии в файле и добавляет ее в конец списка """
    json_saver = JSONSaver()
    vacancies_from_file = json_saver.load_vacancies()
    if len(vacancies_from_file) == 0:
        json_saver.save_list_vacancies(vacancies_list)
        print(vacancies_list)
        print('-' * 100)
        if vacancies_from_file:
            print(vacancies_from_file)
            print('-' * 100)
        return
    # Формируем подписи для старых и новых вакансий
    signatures_from_file = set(f"{v.name}-{v.url}" for v in vacancies_from_file)
    logger.info('Успех в Формировании подписи для старых и новых вакансий')

    # Добавляем только те вакансии, которых еще нет в файле
    new_unique_vacancies = [v for v in vacancies_list if f"{v.name}-{v.url}" not in signatures_from_file]
    logger.info('Успех. Отобраны вакансии, которых еще нет в файле в отдельную переменную')

    # Добавляем новые вакансии в файл
    try:
        json_saver.add_vacancy(list(new_unique_vacancies))
        logger.info('Успех в Добавлении уникальных вакансий в файл')
    except TypeError as e:
        logger.error(f'Провал вакансии не добавлены по причине: {e}, new_unique_vacancies {type(new_unique_vacancies)}')


def menu():
    # Запрос города для дальнейшей сортировки полученных данных
    city = input('Выберите город (не обязательно): ')
    # Получение вакансий
    while True:
        vacancies = user_job_request()
        if vacancies == 0:
            return None
        if vacancies:
            break
    logger.info('Успех. Получение вакансий')
    # Активация объекта для работы с данными сохранения в файл
    proc = JSONSaver()
    logger.info('Успех. Активация объекта для работы с данными сохранения в файл')
    # Преобразование донных в список объектов
    vacancies_list = proc.cast_to_object_list(vacancies)
    logger.info('Успех. Преобразование донных в список объектов')

    # Фильтрация по выбранному городу
    sorted_by_city = []
    try:
        sorted_by_city = sort_by_city(vacancies_list, city)
    except ValueError as e:
        print(f'{e}')
    except TypeError as e:
        print(f'{e}')
    logger.info('Успех. Фильтрация по выбранному городу')

    # Добавление отсутствующих вакансий в файл
    if sorted_by_city:
        # print(f'До сортировки по городу список: {sorted_by_city}')
        # print('-' * 100)
        adding_new_vacancies_to_file(list(sorted_by_city))

        # print(f'После сортировки по городу список: {sorted_by_city}')
        # print('+' * 100)


if __name__ == '__main__':
    try:
        menu()
    except KeyboardInterrupt as e:
        print(e)


#######################################################################################################
