import json
import os

from trasformation.data_processor import DataProcessor, AdditionalPropertiesDataProcessor
from trasformation.xml_reader import XMLParser



if __name__ == '__main__':
    # Загрузка конфигурации
    with open('config.json', 'r', encoding='utf-8') as config_file:
        config = json.load(config_file)

    #Ссылки на файл для теста
    # xml_path = "exemple//1709127537_skus.xml"  # Указать путь к вашему XML файлу
    # xml_path = "exemple//1708931814_import_Bitrix_Sales_full.xml"  # Указать путь к вашему XML файлу
    xml_path = "exemple//1709266229_prices.xml"  # Указать путь к вашему XML файлу

    #Создаем обработчик XML
    parser = XMLParser(xml_path)
    json_data = parser.parse()
    filename = os.path.basename(xml_path)
    #Создаем арсер данных
    #processor = SalesDataProcessor(config['SalesProcessing'])
    # processor = AdditionalPropertiesDataProcessor(config['AdditionalPropertiesProcessing'])
    processor = DataProcessor(config['PricesProcessing'],filename)
    # processor = DataProcessor(config['SKUProcessing'])
    # processor = AdditionalPropertiesDataProcessor(config['SKUSolutionsProcessing'])
    processed_sales = processor.get_data(json.loads(json_data))
    # processed_sales = processor.process(json.loads(json_data))

    for dat in processed_sales:
        print(dat)

