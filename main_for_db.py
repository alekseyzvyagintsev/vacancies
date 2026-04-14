########################################################################
import os

from dotenv import load_dotenv
from src.hh_api_interaction import HeadHunterAPI
from src.vacancies import JSONSaver
from src.db_manager import DBManager

# Параметры подключения к базе данных
load_dotenv(override=True)

db_params = {
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'port': os.getenv('DB_PORT'),
}

# Экземпляр класса для работы с базой данных
dbm = DBManager(db_params)

# Открываем соединение и создаем базу данных + таблицы
dbm.initialize_database()

# Экземпляр класса для работы с API сайтов с вакансиями
hh_api = HeadHunterAPI()

# Экземпляр класса для работы с данными json
json_data = JSONSaver()

# Функция для взаимодействия с пользователем


def user_interaction():

    # Получение вакансий с hh.ru в формате JSON
    profession = "разработчик"
    hh_vacancies = hh_api.get_vacancies(profession)

    # Преобразование набора данных из JSON в список объектов
    vacancies_list = json_data.cast_to_object_list(hh_vacancies)

    while True:
        user_input = input("Введите количество вакансий (не менее 10) для вывода в топ N: ")
        try:
            if int(user_input) >= 10:
                top_n = abs(int(user_input))
                break  # Выход из цикла, если ввод правильный
            elif 0 < int(user_input) < 10:
                top_n = 10
                break  # Выход из цикла, если ввода не последовало
        except ValueError:
            print("Некорректный ввод! Введите целое положительное число.")
    # filter_words = input("Введите ключевые слова для фильтрации вакансий: ")
    salary_range = input("Введите диапазон зарплат: ")  # Пример: 100000-150000

    # Выбираем рублевую зону
    filtered_vacancies = json_data.filter_by_criteria('RUR', vacancies_list)
    # Сортируем по уровню зарплаты
    ranged_vacancies = json_data.get_vacancies_in_salary_range(filtered_vacancies, salary_range)

    top_vacancies = json_data.get_top_vacancies(ranged_vacancies, top_n)
    # json_data.print_vacancies(top_vacancies)
    for vacancy in top_vacancies:
        # Получение вакансий работодателя с hh.ru в формате JSON
        employer_vacancies = hh_api.get_vacancies(url=vacancy.vacancies_url)
        # Преобразование набора данных из JSON в список объектов
        emp_vac_list = json_data.cast_to_object_list(employer_vacancies)
        # json_data.print_vacancies(emp_vac_list)
        for emp_vac in emp_vac_list:
            dbm.insert_data(emp_vac)

    while True:
        print(
            """
            ---------------------------------------------------
                          Выберите пункт меню.
            ---------------------------------------------------
            1. Список компаний и количество вакансий.
            2. Список вакансий.
            3. Среднюю зарплату по вакансиям.
            4. Список вакансий, у которых зарплата выше средней.
            5. Список определенных вакансий.
            0. Выйти
            """
        )
        user_choice = input("Ваш выбор - ").strip()
        try:
            if user_choice == '1':
                companies_data = dbm.get_companies_and_vacancies_count()
                print("\nСписок компаний и количество вакансий:\n")
                for company in companies_data:
                    print(f"{company['company']}: {company['vacancies_count']} вакансий")
            elif user_choice == '2':
                vacancies = dbm.get_all_vacancies()
                print("\nСписок вакансий:\n")
                for vacancy in vacancies:
                    print(f"{vacancy['company']}, {vacancy['job_title']} - {vacancy['salary']} ({vacancy['link']})")
            elif user_choice == '3':
                avg_salary = dbm.get_avg_salary()
                print(f"\nСредняя зарплата: {avg_salary:.2f}")
            elif user_choice == '4':
                high_salary_vacancies = dbm.get_vacancies_with_higher_salary()
                print("\nСписок вакансий, у которых зарплата выше средней:\n")
                for vacancy in high_salary_vacancies:
                    print(vacancy)
            elif user_choice == '5':
                keyword = input("Введите название профессии - ")
                matching_vacancies = dbm.get_vacancies_with_keyword(keyword)
                print(f"\nСписок вакансий содержащие в названии {keyword}:\n")
                for vacancy in matching_vacancies:
                    print(vacancy)
            elif user_choice == '0':
                print("\nВыход из программы.")
                break
            else:
                print("\nНеверный выбор пункта меню. Попробуйте ещё раз!")

        except ValueError:
            print("\nНекорректный ввод! Введите целое положительное число.")


# Закрытие соединения с базой данных
dbm.finalize()

if __name__ == "__main__":
    try:
        user_interaction()
    except KeyboardInterrupt:
        print('\nПриложение завершил пользователь.')
########################################################################
