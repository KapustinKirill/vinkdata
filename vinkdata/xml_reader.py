#xml_reader.py
from collections import defaultdict
from io import BytesIO
from lxml import etree
import io
import xml.etree.ElementTree as ET
import json

def clean_and_parse_xml(file_buffer):
    file_buffer.seek(0)
    content = file_buffer.read()
    content = content.lstrip(b'\xef\xbb\xbf').lstrip(b'\t\r\n')
    file_like_object = io.BytesIO(content)
    tree = etree.parse(file_like_object)
    return tree

class XMLParser:
    def __init__(self, xml_path: str):
        self.xml_path = xml_path

    def clean_content(self, content: bytes) -> bytes:
        return content.lstrip(b'\xef\xbb\xbf').lstrip(b'\t\r\n')

    def parse_from_stream(self, stream: BytesIO) -> str:
        cleaned_content = self.clean_content(stream.getvalue())
        file_like_object = BytesIO(cleaned_content)
        tree = ET.parse(file_like_object)
        root = tree.getroot()


        # Рекурсивная функция для преобразования XML в словарь
        def element_to_dict(element):
            # Создаем словарь атрибутов элемента
            dict_attrs = element.attrib
            if dict_attrs:
                dict_data = {element.tag: {"attributes": dict_attrs}}
            else:
                dict_data = {element.tag: {}}

            children = list(element)
            if children:
                dd = defaultdict(list)
                for dc in map(element_to_dict, children):
                    for k, v in dc.items():
                        dd[k].append(v)
                dict_data[element.tag].update({k: v[0] if len(v) == 1 else v for k, v in dd.items()})
            elif not element.text or not element.text.strip():
                # Если у элемента нет дочерних элементов и текста, то возвращаем только атрибуты
                return dict_data
            else:
                # Если у элемента нет дочерних элементов, но есть текст, добавляем текст в словарь
                text = element.text.strip()
                dict_data[element.tag] = text if not dict_attrs else {"attributes": dict_attrs, "text": text}

            return dict_data

        # Преобразование корневого элемента XML в словарь
        result_dict = element_to_dict(root)

        # Преобразование словаря в JSON
        json_data = json.dumps(result_dict, indent=4, ensure_ascii=False)
        return json_data



    def parse(self) -> str:
        with open(self.xml_path, 'rb') as file:
            raw_content = file.read()
            cleaned_content = self.clean_content(raw_content)
            file_like_object = BytesIO(cleaned_content)
            tree = ET.parse(file_like_object)
            root = tree.getroot()


        # Рекурсивная функция для преобразования XML в словарь
        def element_to_dict(element):
            # Создаем словарь атрибутов элемента
            dict_attrs = element.attrib
            if dict_attrs:
                dict_data = {element.tag: {"attributes": dict_attrs}}
            else:
                dict_data = {element.tag: {}}

            children = list(element)
            if children:
                dd = defaultdict(list)
                for dc in map(element_to_dict, children):
                    for k, v in dc.items():
                        dd[k].append(v)
                dict_data[element.tag].update({k: v[0] if len(v) == 1 else v for k, v in dd.items()})
            elif not element.text or not element.text.strip():
                # Если у элемента нет дочерних элементов и текста, то возвращаем только атрибуты
                return dict_data
            else:
                # Если у элемента нет дочерних элементов, но есть текст, добавляем текст в словарь
                text = element.text.strip()
                dict_data[element.tag] = text if not dict_attrs else {"attributes": dict_attrs, "text": text}

            return dict_data

        # Преобразование корневого элемента XML в словарь
        result_dict = element_to_dict(root)

        # Преобразование словаря в JSON
        json_data = json.dumps(result_dict, indent=4, ensure_ascii=False)
        return json_data

