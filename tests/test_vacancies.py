##############################################################################################################
# import os
import json
import tempfile
from pathlib import Path

import pytest

# from typing import List
# from datetime import datetime
# from unittest.mock import MagicMock, patch
from src.vacancies import JSONSaver, Vacancy

# from src.logging_api import logger


# Множество фикстур и вспомогательных функций для тестов
@pytest.fixture
def temp_json_file():
    with tempfile.NamedTemporaryFile(suffix=".json", mode="w+", dir="./tests/data/", delete=True) as tmpfile:
        yield tmpfile.name


@pytest.fixture
def sample_vacancy_data():
    return [
        {
            "name": "Тестовая Вакансия",
            "salary": "100000-200000 RUR.",
            "url": "http://example.com/test-job",
            "description": "Описание вакансии",
            "city": "Москва",
        }
    ]


@pytest.fixture
def sample_vacancy_json_response():
    return [
        {
            "name": "Тестовая Вакансия",
            "salary": {"from": 100000, "to": 200000, "currency": "RUR"},
            "alternate_url": "http://example.com/job",
            "description": "Описание вакансии",
            "area": {"name": "Москва"},
        }
    ]


json_saver = JSONSaver("tmp_for_tests")


# Тестовая группа: Инициализация и базовые операции
# Проверка создания экземпляра класса для работы с данными сохранения в файл
def test_create_instance():
    assert isinstance(json_saver, JSONSaver)


# Проверка работы загрузчика данных при пустом файле
def test_load_vacancies_with_empty_file():
    json_saver.save_vacancies([])
    vacancies = json_saver.load_vacancies()
    assert vacancies == []


# Проверка метода сохранения вакансии из json-строки (из списка словарей)
# и соответствие типа загруженного объекта классу Vacancy
def test_save_and_load_vacancies(sample_vacancy_data):
    json_saver.save_vacancies(sample_vacancy_data)
    loaded_vacancies = json_saver.load_vacancies()
    assert len(loaded_vacancies) == 1
    assert isinstance(loaded_vacancies[0], Vacancy)


# Здесь проверяется одновременное добавление объекта вакансия,
# в предварительно затертый файл
# сохранение в методе add_vacancy осуществляется через метод сохранения списка объектов
# проверка путем обратной загрузки из файла и сравнение с ожиданиями
def test_add_vacancy(sample_vacancy_data):
    json_saver.save_vacancies([])
    initial_vacancies = json_saver.load_vacancies()
    assert len(initial_vacancies) == 0
    vacancy_obj = Vacancy(**sample_vacancy_data[0])
    json_saver.add_vacancy(vacancy_obj)
    final_vacancies = json_saver.load_vacancies()
    assert len(final_vacancies) == 1
    assert isinstance(final_vacancies[0], Vacancy)


# Содаем факансию, смотрим файл, удаляем вакансию, смотрим файл
def test_delete_vacancy(sample_vacancy_data):
    json_saver.save_vacancies([])
    vacancy_obj = Vacancy(**sample_vacancy_data[0])
    json_saver.add_vacancy(vacancy_obj)
    initial_vacancies = json_saver.load_vacancies()
    assert len(initial_vacancies) == 1
    json_saver.delete_vacancy(vacancy_obj)
    final_vacancies = json_saver.load_vacancies()
    assert len(final_vacancies) == 0


# Тестовая группа: Работа с сохранением и сериализацией данных
def test_save_list_vacancies(sample_vacancy_data):
    json_saver.save_vacancies([])
    vacancy_obj = Vacancy(**sample_vacancy_data[0])
    json_saver.save_list_vacancies([vacancy_obj])
    saved_data = json.loads(Path(json_saver.get_file_path).read_text())
    assert saved_data["vacancies"][0]["name"] == "Тестовая Вакансия"


def test_cast_to_object_list(sample_vacancy_json_response):
    json_saver.save_vacancies([])
    objects = json_saver.cast_to_object_list(sample_vacancy_json_response)
    assert len(objects) == 1
    assert isinstance(objects[0], Vacancy)
    assert objects[0].name == "Тестовая Вакансия"


# Тестовая группа: Фильтрация данных
def test_filter_by_criteria_single_string(sample_vacancy_data):
    json_saver.save_vacancies([])
    vacancy_obj = Vacancy(**sample_vacancy_data[0])
    json_saver.add_vacancy(vacancy_obj)
    filtered_vacancies = json_saver.filter_by_criteria("Тестовая")
    assert len(filtered_vacancies) == 1
    assert isinstance(filtered_vacancies[0], Vacancy)


def test_filter_by_criteria_multiple_strings(sample_vacancy_data):
    json_saver = JSONSaver()
    json_saver.save_vacancies([])
    vacancy_obj = Vacancy(**sample_vacancy_data[0])
    json_saver.add_vacancy(vacancy_obj)
    filtered_vacancies = json_saver.filter_by_criteria(["Тестовая", "Вакансия"])
    assert len(filtered_vacancies) == 1
    assert isinstance(filtered_vacancies[0], Vacancy)


def test_filter_by_criteria_no_match(sample_vacancy_data):
    vacancy_obj = Vacancy(**sample_vacancy_data[0])
    json_saver.add_vacancy(vacancy_obj)
    filtered_vacancies = json_saver.filter_by_criteria("Нет такого")
    assert len(filtered_vacancies) == 0


# Тестовая группа: Логика удаления дубликатов и уникальные вакансии
def test_find_unique_vacancies(sample_vacancy_data):
    vacancy_obj = Vacancy(**sample_vacancy_data[0])
    unique_vacancies = json_saver.find_unique_vacancies([], [vacancy_obj])
    assert len(unique_vacancies) == 1
    assert isinstance(unique_vacancies[0], Vacancy)


def test_find_unique_vacancies_duplicates(sample_vacancy_data):
    vacancy_obj = Vacancy(**sample_vacancy_data[0])
    duplicate_vacancy = Vacancy(**sample_vacancy_data[0])
    unique_vacancies = JSONSaver.find_unique_vacancies([vacancy_obj], [duplicate_vacancy])
    assert len(unique_vacancies) == 0


##############################################################################################################
