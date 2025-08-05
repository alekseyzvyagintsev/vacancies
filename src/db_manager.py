###############################################################################################
import psycopg2

from src.vacancy import Vacancy


class ConnectionManager:
    """Метод для работы с подключением к базе данных"""

    def __init__(self, db_params: dict) -> None:
        self.db_params = db_params
        self.conn = None

    def connect(self) -> None:
        try:
            self.conn = psycopg2.connect(**self.db_params)
            self.conn.autocommit = True
        except psycopg2.Error as e:
            raise Exception(f"Ошибка подключения к базе данных: {str(e)}")

    def close_connection(self) -> None:
        if self.conn is not None:
            self.conn.close()

    def get_connection(self):
        return self.conn


class DBCreate:
    """Метод для создания базы данных"""

    def __init__(self, connection_manager: ConnectionManager) -> None:
        self.connection_manager = connection_manager

    def create_db(self) -> None:
        # Подключаемся временно к базе данных "postgres"
        temp_params = self.connection_manager.db_params.copy()
        temp_params["database"] = "postgres"

        conn = psycopg2.connect(**temp_params)
        conn.autocommit = True
        try:
            with conn.cursor() as cur:
                cur.execute(f"DROP DATABASE IF EXISTS {self.connection_manager.db_params['database']};")
                cur.execute(f"CREATE DATABASE {self.connection_manager.db_params['database']} ENCODING 'UTF8';")
            print(f"База данных {self.connection_manager.db_params['database']} создана.")
        except psycopg2.Error as e:
            print(str(e))
        finally:
            conn.close()


def ensure_connected(func):
    def wrapper(self, *args, **kwargs):
        if self.connection_manager.conn.closed != 0:
            self.connection_manager.connect()
        return func(self, *args, **kwargs)

    return wrapper


class CRUDTables:
    """Класс для работы с таблицами базы банных"""

    def __init__(self, connection_manager: ConnectionManager) -> None:
        self.connection_manager = connection_manager

    def create_tables(self) -> None:
        """
        Метод для создания таблиц employers и vacancies
        """
        try:
            with self.connection_manager.get_connection().cursor() as cur:
                cur.execute("""
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

    @ensure_connected
    def insert_into_tables(self, obj: Vacancy) -> None:
        """
        Метод для добавления данных в таблицы
        """
        conn = self.connection_manager.get_connection()
        try:
            with conn.cursor() as cur:
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
                                """,
                                (obj.employer, obj.employer_id, obj.vacancies_url),
                    )
                    cur.execute("""
                                INSERT INTO vacancies (title, salary, description, city, url, employer_id)
                                VALUES (%s, %s, %s, %s, %s, %s);
                                """,
                                (obj.name, obj.salary, obj.description, obj.city, obj.url, obj.employer_id),
                    )

                # Завершение транзакции
                cur.execute("COMMIT;")
            print("Запись успешно добавлена.")
        except Exception as e:
            if conn.closed == 0:
                conn.rollback()
            else:
                print("Соединение с базой данных было закрыто.")
            print(f"Произошла ошибка: {str(e)}")


class DataAnalyzer:
    """Метод для работы с данными таблиц базы данных"""

    def __init__(self, connection_manager: ConnectionManager) -> None:
        self.connection_manager = connection_manager

    def get_companies_and_vacancies_count(self) -> list:
        """
        Получает список всех компаний и количество вакансий у каждой компании.
        """

        result = []
        try:
            with self.connection_manager.get_connection().cursor() as cur:
                # Выполняем запрос, который агрегирует количество вакансий по каждому работодателю
                cur.execute("""
                            SELECT e.employer AS company_name, COUNT(v.id) AS vacancies_count
                            FROM employers e
                                     LEFT JOIN vacancies v ON e.employer_id = v.employer_id
                            GROUP BY e.employer_id, e.employer
                            ORDER BY e.employer ASC;
                            """
                )
                rows = cur.fetchall()
                for row in rows:
                    result.append({"company": row[0], "vacancies_count": row[1]})
        except Exception as e:
            print(f"Ошибка при выполнении запроса: {str(e)}")
        return result

    def get_all_vacancies(self) -> list:
        """
        Получает список всех вакансий с указанием названия компании, названия вакансии, зарплаты и ссылки на вакансию.
        """
        result = []
        try:
            with self.connection_manager.get_connection().cursor() as cur:
                # Выполняем запрос, который объединяет таблицы vacancies и employers
                cur.execute("""
                            SELECT e.employer, v.title, v.salary, v.url      
                            FROM vacancies v
                                     INNER JOIN employers e ON v.employer_id = e.employer_id
                            ORDER BY e.employer ASC;
                            """
                )
                rows = cur.fetchall()
                for row in rows:
                    result.append({"company": row[0], "job_title": row[1], "salary": row[2], "link": row[3]})
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
            with self.connection_manager.get_connection().cursor() as cur:
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
                            """
                )
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
            with self.connection_manager.get_connection().cursor() as cur:
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
                            """
                )
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
            with self.connection_manager.get_connection().cursor() as cur:
                # Используем регулярное выражение с регистронезависимым поиском
                cur.execute("""
                            SELECT title, salary, url
                            FROM vacancies
                            WHERE LOWER(title) LIKE %s;
                            """, (f"%{keyword.lower()}%",),
                )
                    

                rows = cur.fetchall()
                for row in rows:
                    result.append(f"{row[0]}, {row[1]}, {row[2]}")
        except Exception as e:
            print(f"Ошибка при выполнении запроса: {str(e)}")
        return result


class DBManager:
    def __init__(self, db_params: dict) -> None:
        self.connection_manager = ConnectionManager(db_params)
        self.crud_tables = CRUDTables(self.connection_manager)
        self.data_analyzer = DataAnalyzer(self.connection_manager)

    def initialize_database(self):
        self.connection_manager.connect()
        self.crud_tables.create_tables()

    def finalize(self):
        self.connection_manager.close_connection()

    def insert_data(self, obj: Vacancy) -> None:
        self.crud_tables.insert_into_tables(obj)

    def get_companies_and_vacancies_count(self) -> list:
        return self.data_analyzer.get_companies_and_vacancies_count()

    def get_all_vacancies(self) -> list:
        return self.data_analyzer.get_all_vacancies()

    def get_avg_salary(self) -> float:
        return self.data_analyzer.get_avg_salary()

    def get_vacancies_with_higher_salary(self) -> list:
        return self.data_analyzer.get_vacancies_with_higher_salary()

    def get_vacancies_with_keyword(self, keyword) -> list:
        return self.data_analyzer.get_vacancies_with_keyword(keyword)


###############################################################################################
