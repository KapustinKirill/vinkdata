import json
import os


class JSONParser:
    def __init__(self, json_path: str):
        self.json_path = json_path

    def parse(self) -> dict:
        if not os.path.exists(self.json_path):
            raise FileNotFoundError(f"Файл {self.json_path} не найден.")

        with open(self.json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        return data
