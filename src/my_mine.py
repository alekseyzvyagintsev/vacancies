#######################################################################################################
from requests import HTTPError

from src.logging_main import logger
from src.hh_api_interaction import HeadHunterAPI
from src.vacancies import JSONSaver


def user_job_request(keyword, amount=None):
    """ Получение вакансий через API во запросу пользователя"""
    global hh_api

    try:
        logger.info('Создание экземпляра класса для работы с API сайтов с вакансиями')
        hh_api = HeadHunterAPI()
    except HTTPError as e:
        logger.error(f'Произошла ошибка: {e}')
    try:
        logger.info('Получаем данные через API')
        vacancies = hh_api.get_vacancies(keyword, amount)
        return vacancies
    except Exception as e:
        logger.error(f'Произошла ошибка: {e}')
        return None


def menu():
    """ Диалог с пользователем для получения вакансий по API или из файла"""

    # Выбор варианта запроса вакансий от сайта, из файла или отказ и выход из программы
    global hh_api, vacancies_list
    print('\nДля получения вакансий сделайте выбор.')
    print('1. Поиск вакансий на hh.ru')
    print('2. Работа с локальными данными')
    print('0. Выход из программы.')

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

    while True:
        keyword = input('Введите поисковый запрос (например: Python разработчик): ')
        if len(keyword) > 0:
            break
    while True:
        user_input = input("Введите количество вакансий для вывода в топ N: ")
        try:
            if user_input != '0':
                top_n = abs(int(user_input))
                break  # Выход из цикла, если ввод правильный
        except ValueError:
            print("Некорректный ввод! Введите целое положительное число.")
    filter_words = input("Введите ключевые слова для фильтрации вакансий: ").split()
    salary_range = input("Введите диапазон зарплат: ") # Пример: 100000-150000

    logger.info('Получение вакансий')
    # Создание экземпляра класса для работы с данными сохранения в файл
    proc = JSONSaver()

    if user_choice == 1:
        # Переменную количество объявлений делаем необязательной
        try:
            amount = int(input('Сколько вакансий получить на сайте (не обязательно)?: '))
        except ValueError:
            logger.info('Принимаются только числа. Введенная строка игнорируется')
            amount = None

        while True:
            logger.info('Получаем от функции user_job_request json-данные через API')
            hh_vacancies = user_job_request(keyword, amount)
            if hh_vacancies == 0:
                return None
            if hh_vacancies:
                break
        logger.info('Преобразование донных в список объектов')
        vacancies_list = proc.cast_to_object_list(hh_vacancies)
    if user_choice == 2:
        # Получаем данные из файла
        local_vacancies = proc.load_vacancies()
        vacancies_list = proc.filter_by_criteria(keyword, local_vacancies)
        if not vacancies_list:
            logger.info(f'Файл пуст {vacancies_list}')
            print('\nЛокальное источник вакансий оказался пуст,\nвыберите другой источник или выйдите из программы.')
            menu()

    if vacancies_list:
        logger.info('Фильтрация по выбранному критерию')
        filtered_vacancies = proc.filter_by_criteria(filter_words, vacancies_list)

        logger.info('Фильтрация по признаку зарплата в указанном диапазоне')
        ranged_vacancies = proc.get_vacancies_in_salary_range(filtered_vacancies, salary_range)

        logger.info('Сортируем вакансии по убыванию среднего уровня зарплаты')
        sorted_vacancies = proc.sort_vacancies(ranged_vacancies)

        logger.info('Берём первые top_n вакансий из отсортированных')
        top_vacancies = proc.get_top_vacancies(sorted_vacancies, top_n)

        logger.info('Выводим полученный список построчно')
        proc.print_vacancies(top_vacancies)

        logger.info('Добавление отсутствующих вакансий в файл')
        proc.add_vacancy(list(top_vacancies))


if __name__ == '__main__':
    try:
        menu()
    except KeyboardInterrupt as ex:
        logger.error(ex)


#######################################################################################################
