#########################################################################################################
class VacanciesIterator:
    """
        Принимает список вакансий и при переборе выдает по одной
        либо с помощью метода next, либо при внешней итерации VacanciesIterator(list)
    """

    def __init__(self, vacancies_list: list) -> None:
        self.vacancies = vacancies_list
        self.index = 0

    def __iter__(self) -> "VacanciesIterator":
        return self

    def __next__(self) -> str:
        # Проверяем, что передан именно список вакансий
        # if not isinstance(self, list) or not all(isinstance(item, "Vacancy") for item in self):
        #     raise TypeError("Ожидается список объектов класса Vacancy")
        if self.index < len(self.vacancies):
            vacancy = self.vacancies[self.index]
            self.index += 1
            return vacancy
        else:
            raise StopIteration


# if __name__ == '__main__':
#     from src.hh_api_interaction import HeadHunterAPI
#     hh_api = HeadHunterAPI()
#     vacancies = []
#     try:
#         vacancies = hh_api.load_vacancies("Python")
#     except Exception as e:
#         print(f'Произошла ошибка: {e}')
#
#     # print(vacancies)
#
#     iterator = VacanciesIterator(vacancies)
#     print(next(iterator))
#     print(next(iterator))
#
#     for vacancy in iterator:
#         print(vacancy)

#########################################################################################################
