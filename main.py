import json
import os
from datetime import datetime
from pathlib import Path
from config import db_details
from trasformation.data_processor import DataProcessor, AdditionalPropertiesDataProcessor
from trasformation.db_connectors import DatabaseManager
from trasformation.file_processor import FileManager
from trasformation.xml_reader import XMLParser
from config import ftp_details



if __name__ == '__main__':
    # Загрузка конфигурации
    with open('config.json', 'r', encoding='utf-8') as config_file:
        config = json.load(config_file)
    file_manager = FileManager(ftp_details=ftp_details)
    filtered_files = file_manager.list_files(ftp_details['dir']).filter(date__gt=datetime(2024, 2, 1), text__icontains = 'sale').files
    print(filtered_files)
    # Путь к файлу может быть как на FTP, так и локально
    file_path = filtered_files[0]
    # Чтение файла как потока
    file_stream = file_manager.read_file_as_stream(file_path)
    # Создание экземпляра парсера и обработка потока
    xml_parser = XMLParser(file_stream)
    json_data = xml_parser.parse_from_stream(file_stream)
    processor = DataProcessor(config['SalesProcessing'],file_path)
    processed_sales = processor.get_data(json.loads(json_data))
    print(json_data)
    db_connector = DatabaseManager(config["PriceTypesProcessing"], **db_details)
    db_connector.insert_data(processed_sales)


    # #Ссылки на файл для теста
    # # xml_path = "exemple//1709127537_skus.xml"  # Указать путь к вашему XML файлу
    # # xml_path = "exemple//1708931814_import_Bitrix_Sales_full.xml"  # Указать путь к вашему XML файлу
    # xml_path = "exemple//1709266229_prices.xml"  # Указать путь к вашему XML файлу
    #
    # #Создаем обработчик XML
    # parser = XMLParser(xml_path)
    # json_data = parser.parse()
    # filename = os.path.basename(xml_path)
    # #Создаем парсер данных
    # # processor = DataProcessor(config['SalesProcessing'])
    # # processor = AdditionalPropertiesDataProcessor(config['AdditionalPropertiesProcessing'])
    #
    #
    # processor = DataProcessor(config['PriceTypesProcessing'],filename)
    # # processor = DataProcessor(config['SKUProcessing'])
    # #  processor = AdditionalPropertiesDataProcessor(config['SKUSolutionsProcessing'])
    # processed_sales = processor.get_data(json.loads(json_data))
    # # processed_sales = processor.process(json.loads(json_data))
    #
    # for dat in processed_sales:
    #     print(dat)
    # db_connector = DatabaseManager(config["PriceTypesProcessing"], **db_details)
    #     # db_connector.insert_data(processed_sales)
    #
    # processor = DataProcessor(config['PricesProcessing'],filename)
    # # processor = DataProcessor(config['SKUProcessing'])
    # #  processor = AdditionalPropertiesDataProcessor(config['SKUSolutionsProcessing'])
    # processed_sales = processor.get_data(json.loads(json_data))
    # # processed_sales = processor.process(json.loads(json_data))
    #
    # for dat in processed_sales:
    #     print(dat)
    # db_connector = DatabaseManager(config["PricesProcessing"], **db_details)
    # db_connector.insert_data(processed_sales)

    # Для работы с локальными файлами


    # Получение и фильтрация списка файлов
    # # filtered_files = file_manager.list_files(ftp_details['dir']).filter(, text__contains='sku').files
    # filtered_files = file_manager.list_files(ftp_details['dir']).filter(date__gt=datetime(2024, 2, 1)).files
    # print(filtered_files)
    #
    # # Копирование отфильтрованных файлов в локальную директорию
    # file_manager.copy_files_to(filtered_files, 'exemple')

    # Предположим, что у вас есть следующая структура файлов:
    # /my_project/
    #   /files/
    #     20230101_report.txt
    #     20230115_summary.txt
    #     20230201_report.txt
    #     notes.txt

    # relative_path = Path("exemple")
    # absolute_path = relative_path.resolve()
    # print(absolute_path)
    #
    #
    # # Инициализируем FileManager с базовым путем к директории с файлами
    # file_manager = FileManager(base_path=relative_path)
    # relative_path = Path("test")
    # new_absolute_path = relative_path.resolve()
    # # Получаем список файлов и фильтруем их
    # filtered_files = file_manager.list_files().filter(date__gte=datetime(2024, 2, 15), text__contains='sku').files
    #
    # # Копируем отфильтрованные файлы в локальную директорию для последующей обработки
    # file_manager.copy_files_to(filtered_files, new_absolute_path)