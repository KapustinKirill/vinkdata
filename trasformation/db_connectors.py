import json
from contextlib import contextmanager
import psycopg2
from psycopg2.extras import execute_batch

from config import db_details


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

    # def insert_entities_in_batches(cur, table_name, entities_data, schema, conflict_target):
    #     # Строим список столбцов и placeholders из схемы
    #     columns = [col for col, dtype in schema]
    #     placeholders = ", ".join(["%s" for _ in schema])
    #     columns_list = ", ".join(columns)
    #
    #     # Определяем столбцы для обновления, исключая conflict_target
    #     update_columns = [col for col in columns if col != conflict_target]
    #
    #     # Формируем строку SET для обновления
    #     update_set = ", ".join([f"{col} = EXCLUDED.{col}" for col in update_columns])
    #
    #     # Формируем действие при конфликте
    #     conflict_action = f"ON CONFLICT ({conflict_target}) DO UPDATE SET {update_set}" if conflict_target else "ON CONFLICT DO NOTHING"
    #
    #     # Формируем и выполняем запрос
    #     insert_query = f"""
    #     INSERT INTO {table_name} ({columns_list})
    #     VALUES ({placeholders})
    #     {conflict_action};
    #     """
    #
    #     chunk_size = 1000
    #     for i in range(0, len(entities_data), chunk_size):
    #         chunk = entities_data[i:i + chunk_size]
    #         #         print(f"Insert query: {insert_query}")  # Debugging
    #         #         print(f"Sample chunk: {chunk}")  # Debugging, print first element of the chunk
    #         try:
    #             execute_batch(cur, insert_query, chunk)
    #
    #         except Exception as e:
    #             print(f"Ошибка при вставке данных в {table_name}: {e}")
    #             print(f"Данные, вызвавшие ошибку: {chunk[0]}")
    #             print(f"Запрос, вызвавший ошибку: {insert_query}")
    #             break  # Прерываем выполнение, чтобы избежать дальнейших ошибок

    # def insert_entities_in_batches(self, cur, table_name, entities_data, config_key):
    #     config = self.config
    #     fields_config = config['fields']
    #     computed_fields_config = config.get('computed_fields', [])
    #
    #     columns = [field['dest'] for field in fields_config]
    #     placeholders = ", ".join(["%s" for _ in fields_config + computed_fields_config])
    #     columns_list = ", ".join(columns + [cf['dest'] for cf in computed_fields_config])
    #
    #     insert_query = f"INSERT INTO {table_name} ({columns_list}) VALUES ({placeholders})"
    #
    #     chunk_size = 1000
    #     for i in range(0, len(entities_data), chunk_size):
    #         chunk = entities_data[i:i + chunk_size]
    #         values = []
    #         for item in chunk:
    #             row = [item[field['source']] for field in fields_config]
    #             # Добавление вычисляемых полей
    #             for comp_field in computed_fields_config:
    #                 compute_func = getattr(self, comp_field['compute'])
    #                 row.append(compute_func())
    #             values.append(tuple(row))
    #
    #         execute_batch(cur, insert_query, values)

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
            values_list = [tuple(item[col] for col in columns) for item in chunk]

            try:
                execute_batch(cur, insert_query, values_list)
            except psycopg2.DatabaseError as error:
                print(f"Ошибка при вставке данных: {error}")
                break  # Остановить вставку при возникновении ошибки
    def insert_data(self, entites_data):
        with self.connect() as cur:
            self.insert_entities_in_batches(cur, entites_data)


if __name__ == '__main__':
    with open('../config.json', 'r', encoding='utf-8') as config_file:
        config = json.load(config_file)


    entites_data = [
    {'ДатаПродажи': '12.01.2024 12:16:25', 'Номенклатура': 'Холст Indorian натуральный выбеленный, 65% хлопок, 350 г, 1,07*30 м, матовый', 'НоменклатураКод': 'о8750', 'НоменклатураНаименование': 'Холст Indorian натуральный выбеленный, 65% хлопок, 350 г, 1,07*30 м, матовый', 'НоменклатураГУИД': 'f4efd4a5-850f-11ed-af54-000c29083909', 'Количество': '1', 'СуммаПродажи': '124,47', 'ЗаказПокупателя': 'Заказ покупателя Г-Л01709 от 12.01.2024 12:11:09', 'ЗаказПокупателяНомер': 'Г-Л01709', 'ЗаказПокупателяОрганизация': 'Винк ООО', 'ОрганизацияГУИД': '196e0c68-c4d2-11e1-8896-005056c00008', 'ЗаказГУИД': '34142cb0-b119-11ee-bfe4-000c294ae96a', 'ЗаказПокупателяКонтрагент': 'ТОЧКА ОТРЫВА ООО (Спб)', 'КонтрагентГУИД': 'c2cb1712-4047-11e7-bffb-000c293bb9ea', 'ЗаказПокупателяКонтрагентПартне': None, 'ПартнерГУИД': 'a5fc7669-c661-11e5-a1ba-000c293bb9ea', 'ЗаказПокупателяСклад': 'Петербург', 'ЗаказПокупателяСкладРезки': 'Нет', 'ЗаказПокупателяПодразделение': 'ОП Шушары', 'ЗаказПокупателяСуммаДокумента': '26\xa0551,08', 'ЗаказПокупателяВалютаДокумента': 'RUB', 'ЗаказПокупателяВидОплаты': '1', 'ЗаказПокупателяСпособОплаты': 'По предварительной дог-сти (ИНАЧЕ)', 'ЗаказПокупателяПоИнтернетЗаявке': 'Нет', 'ЗаказПокупателяКонтрагентОсновн': None, 'ЗаказПокупателяДоставка': 'Да', 'ЗаказПокупателяРегионДоставки': 'Санкт-Петербург г', 'ЗаказПокупателяАдресДоставки': '198095, Санкт-Петербург г, Ивана Черных ул, дом № 29', 'ГородДоставки': '', 'РайонДоставки': '', 'ПоселокДоставки': '', 'УлицаДоставки': 'Ивана Черных ул', 'ЗаказПокупателяГрузополучатель': '', 'ЗаказПокупателяИсполнитель': 'Габо Валерия Олеговна', 'Возврат': False, 'hash': '6344a2eeaa91f5906c14883c022f400ff396c26469f4932fa0a942a0abf71ef1'},
    {'ДатаПродажи': '12.01.2024 12:16:25', 'Номенклатура': 'Холст Indorian натуральный выбеленный, 65% хлопок, 350 г, 1,27*30 м, матовый', 'НоменклатураКод': 'о6176', 'НоменклатураНаименование': 'Холст Indorian натуральный выбеленный, 65% хлопок, 350 г, 1,27*30 м, матовый', 'НоменклатураГУИД': 'd1fb57e2-4c51-11ec-b179-000c29083909', 'Количество': '1', 'СуммаПродажи': '147,74', 'ЗаказПокупателя': 'Заказ покупателя Г-Л01709 от 12.01.2024 12:11:09', 'ЗаказПокупателяНомер': 'Г-Л01709', 'ЗаказПокупателяОрганизация': 'Винк ООО', 'ОрганизацияГУИД': '196e0c68-c4d2-11e1-8896-005056c00008', 'ЗаказГУИД': '34142cb0-b119-11ee-bfe4-000c294ae96a', 'ЗаказПокупателяКонтрагент': 'ТОЧКА ОТРЫВА ООО (Спб)', 'КонтрагентГУИД': 'c2cb1712-4047-11e7-bffb-000c293bb9ea', 'ЗаказПокупателяКонтрагентПартне': None, 'ПартнерГУИД': 'a5fc7669-c661-11e5-a1ba-000c293bb9ea', 'ЗаказПокупателяСклад': 'Петербург', 'ЗаказПокупателяСкладРезки': 'Нет', 'ЗаказПокупателяПодразделение': 'ОП Шушары', 'ЗаказПокупателяСуммаДокумента': '26\xa0551,08', 'ЗаказПокупателяВалютаДокумента': 'RUB', 'ЗаказПокупателяВидОплаты': '1', 'ЗаказПокупателяСпособОплаты': 'По предварительной дог-сти (ИНАЧЕ)', 'ЗаказПокупателяПоИнтернетЗаявке': 'Нет', 'ЗаказПокупателяКонтрагентОсновн': None, 'ЗаказПокупателяДоставка': 'Да', 'ЗаказПокупателяРегионДоставки': 'Санкт-Петербург г', 'ЗаказПокупателяАдресДоставки': '198095, Санкт-Петербург г, Ивана Черных ул, дом № 29', 'ГородДоставки': '', 'РайонДоставки': '', 'ПоселокДоставки': '', 'УлицаДоставки': 'Ивана Черных ул', 'ЗаказПокупателяГрузополучатель': '', 'ЗаказПокупателяИсполнитель': 'Габо Валерия Олеговна', 'Возврат': False, 'hash': 'dc7d183b23e261858fdb2345053e6e46a7a896c9b2840df50cc7430910617a5e'}

    ]

    db_connector = DatabaseManager(config["SalesProcessing"], **db_details)
    db_connector.insert_data(entites_data)
