import hashlib
import uuid
import datetime

def preprocess_data(value, data_type):
    #Преобразование данных в зависимости от типа данных указанных в системе
    if value is None:
        return None
    if isinstance(value,dict|tuple|list):
        if len(value) == 0:
            return None
    if data_type == 'numeric':
        if isinstance(value, float):
            return value
        try:
            return float(value.replace("\xa0", "").replace(",", "."))
        except ValueError:
            return None
    elif data_type == 'datetime':
        if isinstance(value, datetime.datetime):
            return value
        try:
            return datetime.datetime.strptime(value, "%d.%m.%Y %H:%M:%S")
        except ValueError:
            raise (ValueError(f"Ошибка при расчете {value} как  {data_type}"))
            return None
    elif data_type == 'timestamp':
        try:
            return datetime.datetime.timestamp(datetime.datetime.strptime(value, "%d.%m.%Y %H:%M:%S"))
        except ValueError:
            raise (ValueError(f"Ошибка при расчете {value} как  {data_type}"))
            return None
    elif data_type == 'text':
        try:
            value = value.strip()
        except:
            pass
        return value
    elif data_type == 'integer':
        if isinstance(value, int):
            return value
        try:
            return int(value.replace("\xa0", "").replace(",", "."))
        except ValueError:
            return None
        except Exception as ex:
            raise (Exception(f"Ошибка при обработке {value} - {ex}"))
    elif data_type == 'boolean':
        if isinstance(value, bool):
            return value
        return value.lower() in ['true', '1', 't', 'y', 'yes','да']
    else:
        return value

class DataProcessor:
    #Основной драйвер для обработки данных на сход ожидает настроечную таблицу
    def __init__(self,  config, filename =''):
        self.config = config
        self.filename = filename
        self.file_timestamp = filename.split('_')[0]

    def is_return(self, item):
        #Нужна только для загрузки продаж - определяет возврат это или нет
        if item['Количество'] and preprocess_data(item['Количество'],'numeric') >= 0:
            return False
        else:
            return True

    def get_hash(self, item):
        # Реализация расчета HASH функции на вход принимает и суммирует все значения в словаре item
        hash_string = "".join(str(value) for value in item.values())
        return hashlib.sha256(hash_string.encode('utf-8')).hexdigest()

    def get_key(self, item):
        # Реализация расчета Key функции на вход принимает и суммирует все значения в словаре item
        string_new = "_".join(str(value) for value in item.values())
        return string_new

    def date_from_name(self, item):
        #Разбирам имя файла и получаем из него дату
        actual_date = datetime.datetime.fromtimestamp(int(self.file_timestamp))
        return actual_date

    def uuid4(self, item=None):
        # Возвращаем новый UUID
        return str(uuid.uuid4())

    def _process_item(self, item):
        processed_item = {}
        for field in self.config['fields']:
            value = preprocess_data(self._get_data_by_path(item, field['source'].split('.')), field['data_type'])
            transform_func = field.get('transform', lambda x: x)
            value = transform_func(value)
            processed_item[field['dest']] = value

        for comp_field in self.config.get('computed_fields', []):
            dest = comp_field['dest']
            compute_func_name = comp_field['compute']
            values_source = {}
            if comp_field['source']:
                for source in comp_field['source'].split('.'):
                    if source in processed_item:
                        values_source[source] = processed_item[source]
                    else:
                        raise KeyError(f"Ошибка:  {source} Нет в {processed_item.keys()}")

            if hasattr(self, compute_func_name):
                compute_func = getattr(self, compute_func_name)
                processed_item[dest] = compute_func(values_source)
            else:
                raise ValueError(f"Compute function '{compute_func_name}' is not defined in DataProcessor.")

        return processed_item

    def process(self, data):
        if isinstance(data, list):
            return [self._process_item(item) for item in data]
        elif isinstance(data, dict):
            return [self._process_item(data)]
        else:
            raise TypeError("Data should be a dictionary or a list of dictionaries. ")
    #
    # def process(self, data):
    #     processed_data = []
    #     if isinstance(data, list):
    #         for item in data:
    #             processed_item = {}
    #             for field in self.config['fields']:
    #                 # Извлечение значения с учетом вложенного пути
    #                 value = preprocess_data(self._get_data_by_path(item, field['source'].split('.')), field['data_type'])
    #                 # Применение функции трансформации, если она указана
    #                 transform_func = field.get('transform', lambda x: x)
    #                 value = transform_func(value)
    #                 processed_item[field['dest']] = value
    #             for comp_field in self.config.get('computed_fields', []):
    #                 dest = comp_field['dest']
    #                 compute_func_name = comp_field['compute']
    #                 if comp_field['source'] !="":
    #                     values_surce = {}
    #                     sources = comp_field['source'].split('.')
    #                     for source in sources:
    #                         if source not in processed_item:
    #                             raise KeyError(source)
    #                         else:
    #                             values_surce[source] = processed_item[source]
    #                 else:
    #                     values_surce={}
    #
    #                 # Проверяем, существует ли метод в текущем экземпляре
    #                 if hasattr(self, compute_func_name):
    #                     compute_func = getattr(self, compute_func_name)
    #                     processed_item[dest] = compute_func(values_surce)  # Передаем весь values_surce для гибкости
    #                 else:
    #                     raise ValueError(
    #                         f"Compute function '{compute_func_name}' is not defined in DataProcessor.")
    #
    #
    #             processed_data.append(processed_item)
    #     elif isinstance(data, dict):
    #         item = data
    #         processed_item = {}
    #         for field in self.config['fields']:
    #             # Извлечение значения с учетом вложенного пути
    #             value = preprocess_data(self._get_data_by_path(item, field['source'].split('.')),
    #                                     field['data_type'])
    #             # Применение функции трансформации, если она указана
    #             transform_func = field.get('transform', lambda x: x)
    #             value = transform_func(value)
    #             processed_item[field['dest']] = value
    #         for comp_field in self.config.get('computed_fields', []):
    #             dest = comp_field['dest']
    #             compute_func_name = comp_field['compute']
    #             if comp_field['source'] != "":
    #                 values_surce = {}
    #                 sources = comp_field['source'].split('.')
    #                 for source in sources:
    #                     if source not in processed_item:
    #                         raise KeyError(source)
    #                     else:
    #                         values_surce[source] = processed_item[source]
    #             else:
    #                 values_surce = {}
    #
    #             # Проверяем, существует ли метод в текущем экземпляре
    #             if hasattr(self, compute_func_name):
    #                 compute_func = getattr(self, compute_func_name)
    #                 processed_item[dest] = compute_func(values_surce)  # Передаем весь values_surce для гибкости
    #             else:
    #                 raise ValueError(
    #                     f"Compute function '{compute_func_name}' is not defined in DataProcessor.")
    #         processed_data.append(processed_item)
    #     return processed_data
    @staticmethod
    def _get_data_by_path(data, path):
        for key in path:
            if key in data:
                try:
                    data = data[key]
                except KeyError as ex:
                    raise KeyError(f"Ошибка KeyError {ex} key = {key} data = {data}")
                except TypeError as ex:
                    raise TypeError(f"Ошибка TypeError {ex} key = {key} data = {data}")
            else:
                return None
        return data

    def get_data(self, data):
        #Определяем какие нам нужны данные для обработки обрабатываем и возвращаем Пользователю
        new_data = self._get_data_by_path(data, self.config['path'].split('.'))
        if new_data:
            result = self.process(new_data)
            return result
        return None




class AdditionalPropertiesDataProcessor(DataProcessor):
    def __init__(self, config):
        if 'parent_path' not in config:
            raise KeyError('Атрибутика полей не соответвует AdditionalPropertiesDataProcessor')
        super().__init__(config)

    def expand_list_items(self, data):
        """
        Разворачивает списки в значениях словарей, создавая новые словари для каждого элемента списка.

        :param data: Список словарей для обработки.
        :return: Новый список словарей с развернутыми значениями списков.
        """
        expanded_data = []
        for item in data:
            # Проверяем, есть ли в словаре значения, являющиеся списками
            list_fields = {k: v for k, v in item.items() if isinstance(v, list)}
            if not list_fields:
                # Если списков нет, добавляем исходный словарь в результат
                expanded_data.append(item)
            else:
                # Для каждого списка в словаре создаем новые словари
                for field, list_values in list_fields.items():
                    for value in list_values:
                        # Создаем новый словарь, который копирует исходный, но с одним значением вместо списка
                        new_item = item.copy()
                        new_item[field] = value
                        # Для остальных полей со списками добавляем только первое значение
                        # Это базовый вариант, возможно, потребуется дополнительная логика
                        for other_field in list_fields:
                            if other_field != field:
                                new_item[other_field] = item[other_field][0] if item[other_field] else None
                        expanded_data.append(new_item)
        return expanded_data

    def get_data(self, data):
        properties =[]
        units_data = self._get_data_by_path(data, self.config['parent_path'].split('.'))
        if isinstance(units_data, dict):
            units_data = [units_data,]
        for unit_data in units_data:
            properties_temp = self._get_data_by_path(unit_data, self.config['path'].split('.'))
            if isinstance(properties_temp, list):
                for dict_ in properties_temp:
                    dict_[self.config['parent_id']] =  self._get_data_by_path(unit_data, self.config['parent'].split('.'))
                properties.extend(properties_temp)
            elif isinstance(properties_temp, dict):
                if len(properties_temp) > 0:
                    properties_temp[self.config['parent_id']] = self._get_data_by_path(unit_data, self.config['parent'].split('.'))
                    properties.append(properties_temp)
        result = self.process(properties)


        check_result = self.expand_list_items(result)
        return check_result

