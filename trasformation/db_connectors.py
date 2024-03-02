from contextlib import contextmanager
import psycopg2
class DatabaseManager:
    def __init__(self, database_name, user_name, password, host='localhost'):
        self.database_name = database_name
        self.user_name = user_name
        self.password = password
        self.host = host

    @contextmanager
    def connect(self):
        conn = psycopg2.connect(dbname=self.database_name, user=self.user_name, password=self.password, host=self.host)
        cur = conn.cursor()
        try:
            yield cur
        except psycopg2.DatabaseError as error:
            conn.rollback()
            print(f"Ошибка базы данных: {error}")
        else:
            conn.commit()
        finally:
            cur.close()
            conn.close()
