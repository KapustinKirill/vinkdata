from contextlib import contextmanager
import psycopg2
from psycopg2.extras import execute_batch


class DatabaseManager:
    def __init__(self, config, dbname, user, password, host='localhost'):
        self.database_name = dbname
        self.user_name = user
        self.password = password
        self.host = host
        self.config = config

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

    def insert_entities_in_batches(self, cur, entities_data ):
        config = self.config
        table_name = config["table_name"]
        conflict_target = config["conflict_target"]
        fields = config["fields"] + config["computed_fields"]

        columns = [field["dest"] for field in fields]
        placeholders = ", ".join(["%s"] * len(fields))
        columns_list = ", ".join(columns)

        conflict_action = f"ON CONFLICT ({conflict_target}) DO UPDATE SET " + ", ".join(
            [f"{col} = EXCLUDED.{col}" for col in columns if col != conflict_target]) if conflict_target else \
            "ON CONFLICT DO NOTHING"

        insert_query = f"INSERT INTO {table_name} ({columns_list}) VALUES ({placeholders}) {conflict_action};"

        chunk_size = 1000  # Размер чанка может быть адаптирован в зависимости от вашей среды и объема данных
        for i in range(0, len(entities_data), chunk_size):
            chunk = entities_data[i:i + chunk_size]
            try:
                values_list = [tuple(item[col] for col in columns) for item in chunk]
            except KeyError as ex:
                raise KeyError(chunk)

            try:
                execute_batch(cur, insert_query, values_list)
            except psycopg2.DatabaseError as error:
                print(f"Ошибка при вставке данных: {error}")
                break  # Остановить вставку при возникновении ошибки
    def insert_data(self, entites_data):
        with self.connect() as cur:
            self.insert_entities_in_batches(cur, entites_data)


