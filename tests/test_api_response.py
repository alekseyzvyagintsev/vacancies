######################################################################################
from unittest.mock import Mock, patch

import pytest

from src.hh_api_interaction import HeadHunterAPI


@pytest.fixture(scope="module")
def headhunter_api():
    """Создает экземпляр HeadHunterAPI"""
    return HeadHunterAPI()


@patch("requests.Session")
def test_connect(mock_session):
    """Тест успешного подключения к API."""
    mock_response = Mock(status_code=200)
    mock_session.return_value.get.return_value = mock_response
    api = HeadHunterAPI()
    response = api._connect()
    assert response.status_code == 200


@patch("requests.Session")
def test_get_vacancies_success(mock_session):
    """Тест успешного получения вакансий."""
    mock_response = Mock(json=lambda: {"items": ["vacancy1"]})
    mock_response.status_code = 200
    mock_session.return_value.get.return_value = mock_response
    api = HeadHunterAPI()
    vacancies = api.get_vacancies(keyword="Python разработчик")
    assert len(vacancies) > 0


@patch("requests.Session")
def test_get_vacancies_invalid_keyword(mock_session):
    """Тест передачи неправильного значения параметра keyword."""
    api = HeadHunterAPI()
    with pytest.raises(ValueError, match=r"Необходимо указать наименование вакансии"):
        api.get_vacancies(keyword="")


@patch("requests.Session")
def test_get_vacancies_server_error(mock_session):
    """Тест случая ошибки сервера при получении вакансий."""
    mock_response = Mock(status_code=500)
    mock_session.return_value.get.return_value = mock_response
    api = HeadHunterAPI()
    with pytest.raises(Exception, match=r"Ошибка подключения к API 500"):
        api.get_vacancies(keyword="Developer")


@patch("requests.Session")
def test_get_vacancies_no_items(mock_session):
    """Тест получения пустых результатов."""
    mock_response = Mock(json=lambda: {})
    mock_response.status_code = 200
    mock_session.return_value.get.return_value = mock_response
    api = HeadHunterAPI()
    vacancies = api.get_vacancies(keyword="не существующее название")
    assert vacancies == [], "При отсутствии вакансий ожидался пустой список"


######################################################################################
