import psycopg2

from src.base_models import DBInteraction
from src.vacancy import Vacancy


class DBManager(DBInteraction):
    def __init__(self, db_params: dict) -> None:
        # Сохраняем параметры
        self.db_params = db_params
        self.conn = None

    def create_db(self) -> None:
        """
        Метод для создания базы данных
        """
        # Временное подключение к базе данных postgres
        temp_params = self.db_params.copy()
        temp_params["database"] = "postgres"
        conn = psycopg2.connect(**temp_params)
        conn.autocommit = True
        try:
            with conn.cursor() as cur:
                cur.execute(f"DROP DATABASE IF EXISTS {self.db_params['database']};")
                cur.execute(f"CREATE DATABASE {self.db_params['database']} ENCODING 'UTF8';")
            print(f"База данных {self.db_params['database']} создана.")
        except psycopg2.Error as e:
            print(str(e))
        finally:
            conn.close()

    def connect(self) -> None:
        """
        Метод для подключения к базе данных
        """
        try:
            self.conn = psycopg2.connect(**self.db_params)
            self.conn.autocommit = True
        except psycopg2.Error as e:
            print(str(e))

    def close_connection(self) -> None:
        """
        Метод для отключения от базы данных
        """
        if hasattr(self, "conn"):
            self.conn.close()

    def create_tables(self) -> None:
        """
        Метод для создания таблиц employers и vacancies
        """
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS employers (
                        employer_id INTEGER PRIMARY KEY,
                        employer VARCHAR(200) NOT NULL,
                        url VARCHAR(250) NOT NULL
                    );
                    CREATE TABLE IF NOT EXISTS vacancies (
                        id SERIAL PRIMARY KEY,
                        title VARCHAR(250) NOT NULL,
                        salary VARCHAR(20) NOT NULL,
                        description TEXT,
                        city VARCHAR(100) NOT NULL,
                        url VARCHAR(250) NOT NULL,
                        employer_id INTEGER REFERENCES employers(employer_id) ON DELETE CASCADE
                    );
                """
                )
            print("Таблицы созданы")
        except psycopg2.Error as e:
            print(str(e))

    def insert_to_tables(self, obj: Vacancy) -> None:
        """
        Метод для добавления данных в таблицы
        """
        try:
            with self.conn.cursor() as cur:
                # Начало транзакции
                cur.execute("BEGIN;")

                # Проверяем существование работодателя
                cur.execute("SELECT employer_id FROM employers WHERE employer_id=%s;", (obj.employer_id,))
                existing_employer = cur.fetchone()

                # Добавляем
                if not existing_employer:
                    cur.execute("""
                                INSERT INTO employers (employer, employer_id, url)
                                VALUES (%s, %s, %s) ON CONFLICT DO NOTHING;
                                """, (obj.employer, obj.employer_id, obj.vacancies_url))

                cur.execute("""
                            INSERT INTO vacancies (title, salary, description, city, url, employer_id)
                            VALUES (%s, %s, %s, %s, %s, %s);
                            """, (obj.name, obj.salary, obj.description, obj.city, obj.url, obj.employer_id))

                # Завершаем транзакцию
                cur.execute("COMMIT;")
            print("Запись успешно добавлена.")
        except Exception as e:
            # Отменяем транзакцию в случае ошибки
            cur.execute("ROLLBACK;")
            print(f"Произошла ошибка: {str(e)}")

    def get_companies_and_vacancies_count(self) -> list:
        """
        Получает список всех компаний и количество вакансий у каждой компании.
        """
        result = []
        try:
            with self.conn.cursor() as cur:
                # Выполняем запрос, который агрегирует количество вакансий по каждому работодателю
                cur.execute("""
                            SELECT e.employer AS company_name, COUNT(v.id) AS vacancies_count
                            FROM employers e
                                     LEFT JOIN vacancies v ON e.employer_id = v.employer_id
                            GROUP BY e.employer_id, e.employer
                            ORDER BY e.employer ASC;
                            """)
                rows = cur.fetchall()
                for row in rows:
                    result.append({
                        "company": row[0],
                        "vacancies_count": row[1]
                    })
        except Exception as e:
            print(f"Ошибка при выполнении запроса: {str(e)}")
        return result

    def get_all_vacancies(self) -> list:
        """
        Получает список всех вакансий с указанием названия компании, названия вакансии, зарплаты и ссылки на вакансию.
        """
        result = []
        try:
            with self.conn.cursor() as cur:
                # Выполняем запрос, который объединяет таблицы vacancies и employers
                cur.execute("""
                            SELECT e.employer, v.title, v.salary, v.url      
                            FROM vacancies v
                                     INNER JOIN employers e ON v.employer_id = e.employer_id
                            ORDER BY e.employer ASC;
                            """)
                rows = cur.fetchall()
                for row in rows:
                    result.append({
                        "company": row[0],
                        "job_title": row[1],
                        "salary": row[2],
                        "link": row[3]
                    })
        except Exception as e:
            print(f"Ошибка при выполнении запроса: {str(e)}")
        return result

    def get_avg_salary(self) -> float:
        """
        Получает среднюю зарплату по вакансиям, используя метод average_salary класса Vacancy.
        """
        total_sum = 0
        count_valid_salaries = 0

        try:
            with self.conn.cursor() as cur:
                # Получаем все вакансии из базы данных
                cur.execute("""
                            SELECT v.title, 
                                   v.salary, 
                                   v.url, 
                                   v.description, 
                                   v.city, 
                                   e.employer, 
                                   e.employer_id, 
                                   e.url
                                    
                            FROM vacancies v
                                     INNER JOIN employers e ON v.employer_id = e.employer_id
                            ORDER BY e.employer ASC;
                            """)
                all_vacancies = cur.fetchall()

            # Перебираем каждую вакансию и применяем метод average_salary
            for row in all_vacancies:
                vacancy_obj = Vacancy(*row)
                valid_salary = vacancy_obj.average_salary()

                if valid_salary != 0:  # Исключаем вакансии с нулевыми зарплатами
                    total_sum += valid_salary
                    count_valid_salaries += 1

            if count_valid_salaries == 0:
                return 0

            average_salary = round(total_sum / count_valid_salaries, 2)
            return average_salary

        except Exception as e:
            print(f"Ошибка при выполнении запроса: {str(e)}")
            return 0

    def get_vacancies_with_higher_salary(self) -> list:
        """
        Получает список всех вакансий, у которых зарплата выше средней по всем вакансиям.
        """
        result = []
        avg_salary = self.get_avg_salary()

        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                            SELECT v.title, 
                                   v.salary, 
                                   v.url, 
                                   v.description, 
                                   v.city, 
                                   e.employer, 
                                   e.employer_id, 
                                   e.url
                                    
                            FROM vacancies v
                                     INNER JOIN employers e ON v.employer_id = e.employer_id
                            ORDER BY e.employer ASC;
                            """)
                all_vacancies = cur.fetchall()

            for row in all_vacancies:
                vacancy_obj = Vacancy(*row)
                current_salary = vacancy_obj.average_salary()
                if current_salary > avg_salary:
                    result.append(f"{row[0]}, {row[1]}, {row[2]}")
        except Exception as e:
            print(f"Ошибка при выполнении запроса: {str(e)}")

        return result

    def get_vacancies_with_keyword(self, keyword: str) -> list:
        """
        Получает список всех вакансий, в названии которых содержится указанный термин.
        """
        result = []
        try:
            with self.conn.cursor() as cur:
                # Используем регулярное выражение с регистронезависимым поиском
                cur.execute("""
                            SELECT title, salary, url
                            FROM vacancies
                            WHERE LOWER(title) LIKE %s;
                            """, (f"%{keyword.lower()}%",))

                rows = cur.fetchall()
                for row in rows:
                    result.append(f"{row[0]}, {row[1]}, {row[2]}")
        except Exception as e:
            print(f"Ошибка при выполнении запроса: {str(e)}")
        return result

    def read_table(self):
        """
        Метод для чтения таблицы
        """
        pass

    def update_table(self):
        """
        Метод для обновления таблицы
        """
        pass

    def clearing_table(self):
        """
        Метод для очистки таблицы
        """
        pass
