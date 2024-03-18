import json
from contextlib import contextmanager
import psycopg2
from psycopg2.extras import execute_batch, DictCursor


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
        cur = conn.cursor(cursor_factory=DictCursor)
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
        if "computed_fields" not in config:
            config["computed_fields"] = []
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
        if entites_data:
            with self.connect() as cur:
                self.insert_entities_in_batches(cur, entites_data)
        else:
            raise Exception("Ошибка при записи в БД, нельзя записать пустоту")

    def fetch_data(self):
        query_config = self.config
        table_name = query_config["source_table_name"]
        fields = ", ".join([f'"{item["source"]}" AS "{item["dest"]}"' for item in query_config["fields"]])
        query = f"SELECT {fields} FROM {table_name};"

        with self.connect() as cur:
            cur.execute(query)
            # Получаем результаты как список словарей
            records = cur.fetchall()
            # Преобразуем каждую запись в словарь
            result = {'result':[dict(record) for record in records]}
            # Сериализуем результат в JSON
            result_json = json.dumps(result, default=str, ensure_ascii=False)  # default=str для обработки datetime и других типов
            return result_json

    def create_table(self, config):
        table_name = config["table_name"]
        fields_config = config["fields"]
        fields_definitions = []

        # Сопоставление пользовательских типов данных с типами данных PostgreSQL
        data_types_mapping = {
            "text": "TEXT",
            "numeric": "NUMERIC",
            "datetime": "TIMESTAMP",
            "uuid": "UUID"
        }

        for field in fields_config:
            data_type = data_types_mapping.get(field["data_type"], "TEXT")
            field_definition = f'"{field["dest"]}" {data_type}'
            fields_definitions.append(field_definition)

        # Создаем определение для первичного ключа или уникального индекса, если указан conflict_target
        if "conflict_target" in config and config["conflict_target"]:
            fields_definitions.append(f'PRIMARY KEY ("{config["conflict_target"]}")')

        fields_definitions_str = ", ".join(fields_definitions)
        create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({fields_definitions_str});"

        with self.connect() as cur:
            cur.execute(create_table_query)
            print(f"Таблица {table_name} успешно создана или уже существовала.")

