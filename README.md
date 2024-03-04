
# Vink Data Transformation Library

## Описание

Vink Data Transformation Library — это Python-библиотека, предназначенная для обработки, трансформации и анализа данных. Эта библиотека особенно полезна для проектов, работающих с XML-данными, файлами различных форматов и базами данных. Библиотека предлагает гибкие инструменты для автоматизации процессов трансформации данных. В основном библиотека предназначена для разбора XML файлов генерируемых 1с и последующей записи в БД как с трансформацией, так и без. 

## Основные компоненты

### XML Reader

Модуль `xml_reader.py` предназначен для чтения и обработки XML-файлов. Он обеспечивает извлечение данных из XML и трансформацию в JSON. При этом он способен частично решить проблему с нетипичными файлами 1с.

### File Processor

Модуль `file_processor.py` предоставляет функциональность для работы с файлами, включая чтение, запись. Основное отличие от обычных файловых менеджеров в возможности фильтрации данных по различным необходимым полям в рамках задачи отбора данных как с FTP, так и локального хранилища.
Сейчас реализованы 2 фильтра по понятию `date` и `text` они определяют критерий, а операнд после `__` логику. Вот операнды для критериев:
* Для поля `date`:
  * `lt` - строго меньше (раньше) чем указанная дата в формате datetime
  * `lte` - меньше (раньше) или равно указанной дате в формате datetime
  * `gt` - строго больше (после) чем указанная дата в формате datetime
  * `gte` - больше (после) или равно указанной дате в формате datetime
* Для поля `text`:
  * `contains` - текст содержится в имени файла (регистрозависим)
  * `icontains` - текст содержится в имени файла (регистроНЕзависим)
  * `exact` - строгое соответствие имени файла (регистрозависим)
  * `iexact` - строгое соответствие имени файла (регистроНЕзависим)
  * `notcontains` - текст НЕ содержится в имени файла (регистрозависим)
  * `inotcontains` - текст НЕ содержится в имени файла (регистроНЕзависим)

### DB Connectors

Модуль `db_connectors.py` упрощает работу с базами данных, предоставляя инструменты для установления соединений, На данный момент работает только с POSTGRES так как нужна только она. Основной функционал с записью больших обьемов даных в БД.

### Data Processor

Модуль `data_processor.py` включает в себя набор функций для обработки и трансформации данных, полученных из файлов. Умеет как обрабатывать текущие данные, так и генерировать новые добавляя свои данные или трансформируя текущие, в том числе и созданные им самим.

## Установка

Для установки библиотеки используйте следующую команду:

```bash
pip install git+https://github.com/KapustinKirill/vink_data_transform.git
```

## Настройка

Перед использованием библиотеки необходимо создать и настроить файлы `config.json` и `config.py` (не включены в репозиторий из-за `.gitignore`) для корректной работы с вашими данными и базами данных.

#### Вот пример содержимого `config.json`
```json
{"PricesProcessing": {
    "table_name": "project_schema.Цены",
    "conflict_target":"",
    "path": "БазоваяСтруктура.СписокЦен.Цена",
    "fields": [

      {"source": "ИдСку", "dest": "ИдСку", "data_type": "uuid"},
      {"source": "ИдТипаЦены", "dest": "ИдТипаЦены", "data_type": "uuid"},
      {"source": "Цена", "dest": "Цена", "data_type": "numeric"},
      {"source": "КодВалюты", "dest": "КодВалюты", "data_type": "text"},
      {"source": "КодЕдиницыИзмерения", "dest": "КодЕдиницыИзмерения", "data_type": "integer"}

    ],
    "computed_fields": [
            {"source": "", "dest": "Дата", "data_type": "timestamp","compute": "date_from_name"},
            {"source": "", "dest": "Ид", "data_type": "uuid","compute": "uuid4" }
    ]}}
```
Тут описана таблица `Цены`: 
* Поле "table_name" в какую таблицу ее надо записать полученные данные;
* Поле "conflict_target" отвечает за действия при конфлите при записи;
* Поле "path" где именно в xml файле лежат указанные данные;
* Группа "fields" - какие поля необходимо взять, если данные лежат не в самом поле, а внутри тега необходимо использовать конструкцию "attributes.ЗаказГУИД" что позволит получить данные из словаря тега;
  * Поле "source" в группе "fields" определяет источник данных;
  * Поле "dest" определят в какую колонку таблицы мы хотим сохранить данные;
  * Поле "data_type" отвечает в какой формат система попробует перевести данные;
  * Добавочное поле "transform" попробует произвести трансформацию прямо при загрузке (требует тестирования);
* Группа "computed_fields" - список вычисляемых полей, Доступен мультиввод через `.`, используются именно значения из "dest". В расчете могут быть использованы только предописанные методы класса;  
  * Поле "compute" указывает на метод который должен быть исользован. Вот текущие методы:
    * `date_from_name`  - вставит дату и время из названия файла, источник не требует;
    * `uuid4` - генерирует уникальный uuid4, источник не требует;
    * `get_hash` - расчитает hash функцию для выбранных источников данных. Данные будут переведены в `str` и после этого произведет расчет. Пример поля source c переменными: "ЗаказГУИД.НоменклатураГУИД.Возврат" В данном примере мы создаем хеш функцию состоящую из Заказа, Строки заказа и признака возврата в ней;
    * `is_return` - определяет явлиятся ли строка заказа возвратом. Логика простая если Количество меньше 0 - возвращает True иначе False. Требует поля 'Количество';

Таких таблиц может быть множество по их названию определяется все настройки.
#### Вот пример содержимого `config.py`

```python
# Учетные данные
ftp_details = {
   'host':  "__.__.__.__",
   'user': "user",
   'pass': "password",
   'dir': "/files"
}

db_details = {
   'dbname': "name",
   'user': "user",
   'password': "password",
   'host': "__.__.__.__"
}
```


## Примеры использования

Пример использования модуля `xml_reader`:

```python
from vinkdata.xml_reader import XMLReader

xml_parser = XMLParser(file_stream)
json_data = xml_parser.parse_from_stream(file_stream)
```

Пример использования модуля `data_processor`:

```python
from vinkdata.data_processor import DataProcessor

processor_price = DataProcessor(config['PricesProcessing'],filename)
processed_price_data = processor_price.get_data(json.loads(json_data))
```

## Разработка и вклад

Мы открыты к вашим предложениям и улучшениям. Если вы хотите внести свой вклад в развитие проекта, пожалуйста, создайте pull request или issue в нашем GitHub-репозитории. Максим, это я тебе :)

## Лицензия

Только для внутреннего пользования.
