import json
from time import sleep

import requests


class APIParser:

    TIMEOUT = 600

    def __init__(
            self,
            url: str,
            headers: dict | None = None,
            params: dict | None = None,
            method: str = 'get',
            json_send: dict | None = None,
            send_page_fields_in_params: bool = False,
            base_result_field: str = '',
            throttling: float = 0):
        self.url = url
        self.headers = headers
        self.method = method
        self.json_send = json_send
        self.params = params
        self.base_result_field = base_result_field
        self.send_page_fields_in_params = send_page_fields_in_params
        self.throttling = throttling

    def get_from_sending_page_field(self, parameter):
        if self.send_page_fields_in_params:
            return self.params[parameter]
        return self.json_send[parameter]

    def set_to_sending_page_field(self, parameter, value):
        if self.send_page_fields_in_params:
            self.params[parameter] = value
            return
        self.json_send[parameter] = value

    def throttling_pause(self):
        if self.throttling:
            sleep(self.throttling)

    def parse(self) -> str:
        response = requests.request(method=self.method,
                                    url=self.url,
                                    headers=self.headers,
                                    json=self.json_send,
                                    params=self.params,
                                    timeout=self.TIMEOUT)
        response.raise_for_status()
        return response.text

    def get_from_received(self, data, field):
        if self.base_result_field:
            return data[self.base_result_field][field]
        if not field:
            data
        return data[field]


class APIBasePaginationParser(APIParser):

    def parse(
            self,
            page_field_name: str,
            items_field_name: str,
            amount_of_page: int | None = None,
            page_count_field_name: str | None = None,
            end_page_field_name: str | None = None):
        if (not amount_of_page and
                not end_page_field_name and
                not page_count_field_name):
            return None
        is_continue_needed = True
        data = {}
        while is_continue_needed:
            try:
                page_str = super().parse()
            except requests.exceptions:
                is_continue_needed = False
                break
            page_dict = json.loads(page_str)
            if end_page_field_name:
                if end_page_field_name not in self.get_from_received(
                        page_dict, None):
                    is_continue_needed = False
                    break
                if self.get_from_sending_page_field(
                    page_field_name) >= self.get_from_received(
                        page_dict, end_page_field_name):
                    is_continue_needed = False
            if amount_of_page:
                if self.get_from_sending_page_field(
                        page_field_name) >= amount_of_page:
                    is_continue_needed = False
            if page_count_field_name:
                if page_count_field_name not in self.get_from_received(
                        page_dict, None):
                    is_continue_needed = False
                    break
                if not self.get_from_received(
                        page_dict, page_count_field_name):
                    is_continue_needed = False
            if items_field_name not in data:
                data[items_field_name] = []
            data[items_field_name].extend(
                self.get_from_received(
                    page_dict, items_field_name))
            self.set_to_sending_page_field(
                page_field_name,
                self.get_from_sending_page_field(page_field_name) + 1)
            self.throttling_pause()
        return json.dumps(data)


class APICursorPaginationParser(APIParser):

    def parse(self, cursor_field_name: str, items_field_name: str):
        is_continue_needed = True
        data = {}
        while is_continue_needed:
            try:
                page_str = super().parse()
            except requests.exceptions:
                is_continue_needed = False
                break
            page_dict = json.loads(page_str)
            if not len(self.get_from_received(page_dict, items_field_name)):
                is_continue_needed = False
            self.set_to_sending_page_field(
                cursor_field_name, self.get_from_received(
                    page_dict, cursor_field_name))
            if items_field_name not in data:
                data[items_field_name] = []
            data[items_field_name].extend(
                self.get_from_received(
                    page_dict, items_field_name))
            self.throttling_pause()
        return json.dumps(data)


class APILimitOffsetPaginationParser(APIParser):

    def parse(
            self,
            limit_field_name: str,
            offset_field_name: str,
            items_field_name: str):
        is_continue_needed = True
        data = {}
        while is_continue_needed:
            try:
                page_str = super().parse()
            except requests.exceptions:
                is_continue_needed = False
                break
            page_dict = json.loads(page_str)
            if not len(self.get_from_received(page_dict, items_field_name)):
                is_continue_needed = False
            self.set_to_sending_page_field(
                offset_field_name,
                self.get_from_sending_page_field(offset_field_name) +
                self.get_from_sending_page_field(limit_field_name))
            if items_field_name not in data:
                data[items_field_name] = []
            data[items_field_name].extend(
                self.get_from_received(
                    page_dict, items_field_name))
            self.throttling_pause()
        return json.dumps(data)
