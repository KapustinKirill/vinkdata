import csv
import io
import os
from typing import List, Dict


class CSVParser:
    def __init__(self, file_path: str = None, stream: io.StringIO = None, delimiter: str = ',',
                 encoding: str = 'utf-8'):
        self.file_path = file_path
        self.stream = stream
        self.delimiter = delimiter
        self.encoding = encoding

    def parse(self) -> List[Dict[str, str]]:
        if self.file_path and not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Файл {self.file_path} не найден.")

        data = []
        if self.file_path:
            with open(self.file_path, 'r', encoding=self.encoding) as file:
                reader = csv.DictReader(file, delimiter=self.delimiter)
                for row in reader:
                    data.append(row)
        elif self.stream:
            self.stream.seek(0)
            reader = csv.DictReader(self.stream, delimiter=self.delimiter)
            for row in reader:
                data.append(row)
        else:
            raise ValueError("Не указан ни путь к файлу, ни поток для чтения данных.")

        return data
