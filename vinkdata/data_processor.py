import hashlib
import uuid
import datetime

def preprocess_data(value, data_type):
    #Преобразование данных в зависимости от типа данных указанных в системе
    if value is None:
        return None
    if data_type == 'numeric':
        try:
            return float(value.replace("\xa0", "").replace(",", "."))
        except ValueError:
            return None
    elif data_type == 'datetime':
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
            print(value)
        return value
    elif data_type == 'integer':
        try:
            return int(value.replace("\xa0", "").replace(",", "."))
        except ValueError:
            return None
    elif data_type == 'boolean':
        return value.lower() in ['true', '1', 't', 'y', 'yes']
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
            raise TypeError("Data should be a dictionary or a list of dictionaries.")
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
                data = data[key]
            else:
                return None
        return data

    def get_data(self, data):
        #Определяем какие нам нужны данные для обработки обрабатываем и возвращаем Пользователю
        new_data = self._get_data_by_path(data, self.config['path'].split('.'))
        result = self.process(new_data)
        return result




class AdditionalPropertiesDataProcessor(DataProcessor):
    def __init__(self, config):
        super().__init__(config)

    def get_data(self, data):
        properties =[]
        units_data = self._get_data_by_path(data, self.config['parent_path'].split('.'))
        for unit_data in units_data:
            properties_temp = self._get_data_by_path(unit_data, self.config['path'].split('.'))
            if isinstance(properties_temp, list):
                for dict_ in properties_temp:
                    dict_[self.config['parent_id']] = unit_data[self.config['parent']]
                properties.extend(properties_temp)
            elif isinstance(properties_temp, dict):
                properties_temp[self.config['parent_id']] = unit_data[self.config['parent']]
                properties.append(properties_temp)
        result = self.process(properties)
        return result
