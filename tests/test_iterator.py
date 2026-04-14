#####################################################################################################
import pytest

from src.iterator import VacanciesIterator


def test_vacancies_iterator_initialization():
    # Проверка правильной инициализации
    iterator = VacanciesIterator(["job1", "job2"])
    assert isinstance(iterator, VacanciesIterator), "Итератор неправильно инициализируется."


def test_iteration():
    # Проверяем базовую функциональность итератора
    jobs = ["Python Developer", "Data Scientist"]
    iterator = VacanciesIterator(jobs)

    result = []
    for job in iterator:
        result.append(job)

    assert result == jobs, f"Порядок выдачи элементов неверный: {result}"


def test_stop_iteration():
    # Проверяем исключение StopIteration после исчерпания списка
    jobs = ["Frontend Developer"]
    iterator = VacanciesIterator(jobs)

    _ = next(iterator)
    try:
        next(iterator)
        assert False, "Ожидалось исключение StopIteration"
    except StopIteration:
        pass


def test_empty_list():
    # Проверяем поведение с пустым списком
    empty_jobs = []
    iterator = VacanciesIterator(empty_jobs)

    with pytest.raises(StopIteration):
        next(iterator)


#####################################################################################################
