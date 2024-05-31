import hashlib
import json
import uuid
import datetime

def preprocess_data(value, data_type):
    if value is None:
        return None
    if isinstance(value, (dict, tuple, list)) and len(value) == 0:
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
            raise (ValueError(f"Ошибка при расчете {value} как {data_type}"))
            return None
    elif data_type == 'timestamp':
        try:
            return datetime.datetime.timestamp(datetime.datetime.strptime(value, "%d.%m.%Y %H:%M:%S"))
        except ValueError:
            raise (ValueError(f"Ошибка при расчете {value} как {data_type}"))
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
        return value.lower() in ['true', '1', 't', 'y', 'yes', 'да']
    elif data_type == 'json':
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError as ex:
                raise (Exception(f"Ошибка при создании json {value} - {ex}"))
        elif isinstance(value, (dict, list)):
            return value
        else:
            return None
    else:
        return value

class DataProcessor:
    def __init__(self, config, filename=''):
        self.config = config
        self.filename = filename
        self.file_timestamp = filename.split('_')[0] if filename else None

    def is_return(self, item):
        if item['Количество'] and preprocess_data(item['Количество'], 'numeric') >= 0:
            return False
        else:
            return True

    def get_hash(self, item):
        hash_string = "".join(str(value) for value in item.values())
        return hashlib.sha256(hash_string.encode('utf-8')).hexdigest()

    def get_key(self, item):
        string_new = "_".join(str(value) for value in item.values())
        return string_new

    def date_from_name(self, item):
        actual_date = datetime.datetime.fromtimestamp(int(self.file_timestamp))
        return actual_date

    def uuid4(self, item=None):
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
                        raise KeyError(f"Ошибка: {source} Нет в {processed_item.keys()}")

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
        new_data = self._get_data_by_path(data, self.config['path'].split('.'))
        if new_data:
            result = self.process(new_data)
            return result
        return None

class AdditionalPropertiesDataProcessor(DataProcessor):
    def __init__(self, config):
        if 'parent_path' not in config:
            raise KeyError('Атрибутика полей не соответствует AdditionalPropertiesDataProcessor')
        super().__init__(config)

    def expand_list_items(self, data):
        expanded_data = []
        for item in data:
            list_fields = {k: v for k, v in item.items() if isinstance(v, list)}
            if not list_fields:
                expanded_data.append(item)
            else:
                for field, list_values in list_fields.items():
                    for value in list_values:
                        new_item = item.copy()
                        new_item[field] = value
                        for other_field in list_fields:
                            if other_field != field:
                                new_item[other_field] = item[other_field][0] if item[other_field] else None
                        expanded_data.append(new_item)
        return expanded_data

    def get_data(self, data):
        properties = []
        units_data = self._get_data_by_path(data, self.config['parent_path'].split('.'))
        if isinstance(units_data, dict):
            units_data = [units_data]
        for unit_data in units_data:
            properties_temp = self._get_data_by_path(unit_data, self.config['path'].split('.'))
            if isinstance(properties_temp, list):
                for dict_ in properties_temp:
                    dict_[self.config['parent_id']] = self._get_data_by_path(unit_data, self.config['parent'].split('.'))
                properties.extend(properties_temp)
            elif isinstance(properties_temp, dict):
                if len(properties_temp) > 0:
                    properties_temp[self.config['parent_id']] = self._get_data_by_path(unit_data, self.config['parent'].split('.'))
                    properties.append(properties_temp)
        result = self.process(properties)

        check_result = self.expand_list_items(result)
        return check_result
