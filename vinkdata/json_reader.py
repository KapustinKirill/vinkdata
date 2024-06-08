import json
import os
from io import BytesIO
import ftplib

class JSONParser:
    def __init__(self, json_path: str = None, stream: BytesIO = None):
        self.json_path = json_path
        self.stream = stream

    def parse(self) -> dict:
        if self.json_path:
            if not os.path.exists(self.json_path):
                raise FileNotFoundError(f"Файл {self.json_path} не найден.")
            with open(self.json_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
        elif self.stream:
            self.stream.seek(0)
            data = json.load(self.stream)
        else:
            raise ValueError("Не указан ни путь к файлу, ни поток для чтения данных.")

        return data

    @staticmethod
    def read_json_from_ftp(ftp_details: dict, remote_path: str) -> dict:
        with ftplib.FTP(ftp_details['host'], ftp_details['user'], ftp_details['pass']) as ftp:
            stream = BytesIO()
            ftp.retrbinary(f'RETR {remote_path}', stream.write)
            stream.seek(0)
            data = json.load(stream)
        return data
