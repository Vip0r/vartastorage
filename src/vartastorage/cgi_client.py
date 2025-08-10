import ast
import re
from dataclasses import dataclass, field
from typing import Any

from requests import Response, Session

ERROR_TEMPLATE = "An error occurred while polling {}. Please check your connection"


@dataclass
class CgiData:
    info: dict = field(default_factory=dict)
    service: dict = field(default_factory=dict)
    ems: dict = field(default_factory=dict)
    energy: dict = field(default_factory=dict)


class CgiClient:
    def __init__(self, host, username=None, password=None):
        self.host = host
        self.username = username
        self.password = password

        self.session = Session()

    def get_all_data_cgi(self) -> CgiData:
        out = CgiData()
        out.energy = self.get_energy_cgi()
        out.service = self.get_service_cgi()
        out.ems = self.get_ems_cgi()
        out.info = self.get_info_cgi()
        return out

    def get_energy_cgi(self) -> dict[str, Any]:
        # get energy totals and charge load cycles from CGI
        # "EGrid_AC_DC": 0, "EGrid_DC_AC": 0, "EWr_AC_DC": 0, "EWr_DC_AC": 0,
        # "Chrg_LoadCycles": 0
        return self._get_cgi_as_dict("/cgi/energy.js")

    def get_ems_cgi(self) -> dict[str, Any]:
        # get ems data structure
        # usually a dict of 'wr': {...}, 'charger': [{...}], 'emeter': {...}, 'na': {}
        result: dict[str, Any] = {}

        conf = {
            key.lower(): value
            for key, value in self._get_cgi_as_dict("/cgi/ems_conf.js").items()
        }
        data = {
            key.lower(): value
            for key, value in self._get_cgi_as_dict("/cgi/ems_data.js").items()
        }

        for conf_key, conf_value in conf.items():
            data_key = conf_key.replace("conf", "data")
            if data_key not in data:
                continue

            data_value = data[data_key]
            if len(conf_value) == len(data_value):
                result[conf_key.replace("_conf", "")] = {
                    conf_value[i]: data_value[i] for i in range(0, len(conf_value))
                }
            elif len(data_value) >= 1 and isinstance(data_value[0], list):
                # exception for charger values, this is a list of values
                data_values: list[dict[str, Any]] = []
                for element in data_value:
                    if len(conf_value) != len(element):
                        continue
                    data_values.append(
                        {conf_value[i]: element[i] for i in range(0, len(conf_value))}
                    )
                result[conf_key.replace("_conf", "")] = data_values

        return result

    def get_service_cgi(self) -> dict[str, Any]:
        # get service and maintenance data from CGI
        # "FilterZeit": 0, "Fan": 0, "Main": 0
        return self._get_cgi_as_dict("/cgi/user_serv.js")

    def get_info_cgi(self) -> dict[str, Any]:
        # get various informations by the cgi/info.js
        return self._get_cgi_as_dict("/cgi/info.js")

    def _get_cgi_as_dict(self, path: str) -> dict[str, Any]:
        result = {}
        try:
            response = self._request_data(path)
            response.raise_for_status()
        except Exception as e:
            raise ValueError(ERROR_TEMPLATE.format(path)) from e

        tmp_list = response.text.replace("\n", "").split(";")
        value_list = [value for value in tmp_list if "=" in value]

        for value in value_list:
            splitted = value.split("=", 1)
            result[splitted[0].strip()] = ast.literal_eval(splitted[1].strip())

        return result

    def _request_data(self, urlEnding) -> Response:
        try:
            url = f"http://{self.host}{urlEnding}"
            # Check if a password is set
            if self.password:
                # Password is set so we check if already logged in
                self._check_logged_in()
            return self.session.get(url, timeout=3)
        except Exception as e:
            raise ValueError(ERROR_TEMPLATE) from e

    def _check_logged_in(self):
        pass_url = f"http://{self.host}/cgi/login"
        response = self.session.get(pass_url, timeout=3)
        response.raise_for_status()

        values = re.compile("userlevel = ([0-9]+)")
        results = values.findall(response.text)
        if "2" in results:
            # already logged in
            return True

        login_data = {"user": self.username, "password": self.password}
        response = self.session.post(pass_url, login_data, timeout=3)
        response.raise_for_status()
        return response.status_code == 200
