import pytest
from src.vacancy import Vacancy

# Базовый набор тестовых данных
@pytest.fixture
def simple_vacancy():
    return Vacancy(name="Python-разработчик", salary="50000-80000 руб.", url="https://hh.ru/", description="Опыт программирования на Python", city="Москва")

@pytest.fixture
def another_vacancy():
    return Vacancy(name="JavaScript-разработчик", salary="60000-90000 руб.", url="https://hh.ru/", description="Опыт программирования на JavaScript", city="Санкт-Петербург")

# Тестирование конструктора
def test_constructor(simple_vacancy):
    assert simple_vacancy.name == "Python-разработчик"
    assert simple_vacancy.salary == "50000-80000 руб."
    assert simple_vacancy.url == "https://hh.ru/"
    assert simple_vacancy.description == "Опыт программирования на Python"
    assert simple_vacancy.city == "Москва"

# Тестирование вывода объекта (__repr__)
def test_repr(simple_vacancy):
    representation = repr(simple_vacancy)
    assert "Python-разработчик" in representation
    assert "50000-80000 руб." in representation
    assert "https://hh.ru/" in representation
    assert "Опыт программирования на Python" in representation
    assert "Москва" in representation

# Тестирование формата вывода (__str__)
def test_str(simple_vacancy):
    string_representation = str(simple_vacancy)
    assert "Москва" in string_representation
    assert "Python-разработчик" in string_representation
    assert "50000-80000 руб." in string_representation
    assert "https://hh.ru/" in string_representation
    assert "Опыт программирования на Python" in string_representation

# Тестирование расчета средней зарплаты
def test_average_salary_range():
    vacancy = Vacancy(name="Разработчик", salary="50000-80000 руб.", url="", description="", city="")
    avg_salary = vacancy.average_salary()
    assert avg_salary == 65000.0

def test_average_salary_fixed():
    vacancy = Vacancy(name="Специалист", salary="70000", url="", description="", city="")
    avg_salary = vacancy.average_salary()
    assert avg_salary == 70000.0

def test_average_salary_none():
    vacancy = Vacancy(name="Менеджер", salary=None, url="", description="", city="")
    avg_salary = vacancy.average_salary()
    assert avg_salary == 0

# Тестирование преобразования в словарь
def test_to_dict(simple_vacancy):
    vacancy_dict = simple_vacancy.to_dict()
    assert vacancy_dict["name"] == "Python-разработчик"
    assert vacancy_dict["salary"] == "50000-80000 руб."
    assert vacancy_dict["url"] == "https://hh.ru/"
    assert vacancy_dict["description"] == "Опыт программирования на Python"
    assert vacancy_dict["city"] == "Москва"

# Тестирование воссоздания объекта из словаря
def test_from_dict():
    vacancy_dict = {
        "name": "Python-разработчик",
        "salary": "50000-80000 руб.",
        "url": "https://hh.ru/",
        "description": "Опыт программирования на Python",
        "city": "Москва"
    }
    vacancy = Vacancy.from_dict(vacancy_dict)
    assert vacancy.name == "Python-разработчик"
    assert vacancy.salary == "50000-80000 руб."
    assert vacancy.url == "https://hh.ru/"
    assert vacancy.description == "Опыт программирования на Python"
    assert vacancy.city == "Москва"

# Тестирование оператора меньше (<)
def test_lt_operator(simple_vacancy, another_vacancy):
    assert simple_vacancy < another_vacancy

# Тестирование оператора больше (>)
def test_gt_operator(simple_vacancy, another_vacancy):
    assert another_vacancy > simple_vacancy

# Тестирование оператора равенства (==)
def test_eq_operator():
    vacancy1 = Vacancy(name="QA-инженер", salary="50000-80000 руб.", url="", description="", city="")
    vacancy2 = Vacancy(name="QA-инженер", salary="50000-80000 руб.", url="", description="", city="")
    assert vacancy1 == vacancy2