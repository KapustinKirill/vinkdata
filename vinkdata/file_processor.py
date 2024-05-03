import re
from datetime import datetime
# import os
import shutil
from io import BytesIO
# from config import ftp_details
from pathlib import Path, PurePath
import ftplib

class FileQuerySet:
    def __init__(self, files=None):
        self.files = files or []

    def filter(self, **kwargs):
        filtered_files = self.files
        for attr, value in kwargs.items():
            if "__" in attr:
                field_name, operation = attr.split("__", 1)
                filter_func = self._get_filter_func(field_name, operation, value)
            else:
                filter_func = lambda f, v=value: v in f  # Default filter: check inclusion

            filtered_files = [file for file in filtered_files if filter_func(file)]
        return FileQuerySet(filtered_files)

    def _get_filter_func(self, field_name, operation, value):
        if field_name == "date":
            return self._date_filter(operation, value)
        elif field_name == "text":
            return self._text_filter(operation, value)
        else:
            raise ValueError("Unknown filter field")

    def _date_filter(self, operation, value):
        def parse_date_from_filename(filename):
            filename = Path(filename).name
            match = re.search(r"(\d{10})", filename)
            if match:
                date_str = match.group(1)
                try:
                    if len(date_str) == 13:
                        return datetime.fromtimestamp(int(date_str) / 1000)
                    elif 9 < len(date_str) < 13:
                        return datetime.fromtimestamp(int(date_str))
                    elif len(date_str) == 8:
                        return datetime.strptime(date_str, "%Y%m%d")
                except ValueError:
                    return None
            return None

        if operation == "lt":
            return lambda f: parse_date_from_filename(f) and parse_date_from_filename(f) < value
        elif operation == "lte":
            return lambda f: parse_date_from_filename(f) and parse_date_from_filename(f) <= value
        elif operation == "gt":
            return lambda f: parse_date_from_filename(f) and parse_date_from_filename(f) > value
        elif operation == "gte":
            return lambda f: parse_date_from_filename(f) and parse_date_from_filename(f) >= value
        else:
            raise ValueError("Unsupported date operation")

    def _text_filter(self, operation, value):
        if operation == "contains":
            return lambda f: value in f
        elif operation == "icontains":
            return lambda f: value.lower() in f.lower()
        elif operation == "exact":
            return lambda f: f == value
        elif operation == "iexact":
            return lambda f: f.lower() == value.lower()
        elif operation == "notcontains":
            return lambda f: value not in f
        elif operation == "inotcontains":
            return lambda f: value.lower() not in f.lower()
        else:
            raise ValueError("Unsupported text operation")



class FileManager:
    def __init__(self, base_path=None, ftp_details=None):
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.ftp_details = ftp_details

    def list_files(self, path=''):
        if self.ftp_details:
            files = self._list_files_ftp(path)
        else:
            files = self._list_files_local(path)
        return FileQuerySet(files)

    def _list_files_ftp(self, remote_path):
        with ftplib.FTP(self.ftp_details['host'], self.ftp_details['user'], self.ftp_details['pass']) as ftp:
            ftp.cwd(remote_path)
            files = ftp.nlst()
            return [remote_path + '/' + file for file in files]

    def _list_files_local(self, path):
        full_path = self.base_path / path
        return [str(file) for file in full_path.iterdir() if file.is_file()]

    # def copy_files_to(self, files, target_path):
    #     target_path = Path(target_path)
    #     for file in files:
    #         if self.ftp_details:
    #             self._copy_file_from_ftp(file, target_path / Path(file).name)
    #         else:
    #             shutil.copy(Path(file), target_path / Path(file).name)
    def copy_files_to(self, files, target_path):
        target_path = Path(target_path)
        target_path.mkdir(parents=True, exist_ok=True)  # Создаем целевую директорию, если не существует
        for file in files:
            if self.ftp_details:
                self._copy_file_from_ftp(file, target_path / Path(file).name)
            else:
                shutil.copy(Path(file), target_path / Path(file).name)
        print(f"Copied {len(files)} files to {target_path}")


    def _copy_file_from_ftp(self, remote_file, local_file):
        with ftplib.FTP(self.ftp_details['host'], self.ftp_details['user'], self.ftp_details['pass']) as ftp:
            with open(local_file, 'wb') as f:
                ftp.retrbinary(f'RETR {remote_file}', f.write)

    def read_file_as_stream(self, file_path: str) -> BytesIO:
        filename = Path(file_path).name
        if self.ftp_details:  # Чтение файла с FTP
            with ftplib.FTP(self.ftp_details['host'], self.ftp_details['user'], self.ftp_details['pass']) as ftp:
                stream = BytesIO()
                ftp.retrbinary(f'RETR {file_path}', stream.write)
                stream.seek(0)
                return stream, filename
        else:  # Чтение локального файла
            with open(file_path, 'rb') as file:
                return BytesIO(file.read()), filename


