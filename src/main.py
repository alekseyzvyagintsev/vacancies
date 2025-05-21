from src.hh_api_interaction import HeadHunterAPI
from src.vacancy import Vacancy
from src.vacancies import JSONSaver


# Создание экземпляра класса для работы с API сайтов с вакансиями
hh_api = HeadHunterAPI()

# Получение вакансий с hh.ru в формате JSON
hh_vacancies = hh_api.get_vacancies("Python")

# Преобразование набора данных из JSON в список объектов
vacancies_list = JSONSaver.cast_to_object_list(hh_vacancies)

# Пример работы контструктора класса с одной вакансией
vacancy = Vacancy(
    "Python Developer",
    "100 000-150 000 руб.",
    "<https://hh.ru/vacancy/123456>",
    "Требования: опыт работы от 3 лет...",
    "Москва"
)


# Сохранение информации о вакансиях в файл
json_saver = JSONSaver()
json_saver.add_vacancy(vacancy)
json_saver.delete_vacancy(vacancy)

# Функция для взаимодействия с пользователем
def user_interaction():
    platforms = ["HeadHunter"]
    search_query = input("Введите поисковый запрос: ")
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


    filtered_vacancies = json_saver.filter_by_criteria(filter_words, vacancies_list)

    ranged_vacancies = json_saver.get_vacancies_in_salary_range(filtered_vacancies, salary_range)

    sorted_vacancies = json_saver.sort_vacancies(ranged_vacancies)
    top_vacancies = json_saver.get_top_vacancies(sorted_vacancies, top_n)
    json_saver.print_vacancies(top_vacancies)


if __name__ == "__main__":
    user_interaction()