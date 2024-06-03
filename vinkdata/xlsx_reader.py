import openpyxl
from typing import List, Dict

class XLSXParser:
    def __init__(self, file_path: str, sheet_name: str, header_row: int = 1, data_start_row: int = 2):
        self.file_path = file_path
        self.sheet_name = sheet_name
        self.header_row = header_row
        self.data_start_row = data_start_row

    def parse(self) -> List[Dict[str, str]]:
        workbook = openpyxl.load_workbook(self.file_path, data_only=True)
        sheet = workbook[self.sheet_name]

        # Получение заголовков из указанной строки
        headers = []
        for cell in sheet[self.header_row]:
            headers.append(cell.value)

        data = []
        # Чтение данных начиная с указанной строки
        for row in sheet.iter_rows(min_row=self.data_start_row, values_only=True):
            row_data = {}
            for header, cell_value in zip(headers, row):
                row_data[header] = cell_value
            data.append(row_data)

        return data
