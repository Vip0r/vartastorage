import ast
import re
from dataclasses import dataclass
from typing import Dict

from requests import Response, Session

ERROR_TEMPLATE = "An error occured while polling {}. Please check your connection"

JS_PATTERN_ANY = re.compile("([a-zA-Z0-9_]+) = (.+)?;")
JS_PATTERN_NUMBERS = re.compile("([a-zA-Z0-9_]+) = (-?[0-9\\[\\]]+)?;")


@dataclass
class CgiData:
    EGrid_AC_DC: int = 0
    EGrid_DC_AC: int = 0
    EWr_AC_DC: int = 0
    EWr_DC_AC: int = 0
    Chrg_LoadCycles: int = 0
    FilterZeit: int = 0
    Fan: int = 0
    Main: int = 0


class CgiClient:
    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password

        self.session = Session()

    def get_all_data_cgi(self) -> CgiData:
        out = CgiData()

        print(self.get_ems_cgi())
        print(self.get_energy_cgi())
        print(self.get_info_cgi())
        print(self.get_service_cgi())

        try:
            energytotals = self.get_energy_cgi()
            out.EGrid_AC_DC = energytotals.get("EGrid_AC_DC", 0)
            out.EGrid_DC_AC = energytotals.get("EGrid_DC_AC", 0)
            out.EWr_AC_DC = energytotals.get("EWr_AC_DC", 0)
            out.EWr_DC_AC = energytotals.get("EWr_DC_AC", 0)
            out.Chrg_LoadCycles = energytotals.get("Chrg_LoadCycles", 0)

            servicedata = self.get_service_cgi()
            out.FilterZeit = servicedata.get("FilterZeit", 0)
            out.Fan = servicedata.get("Fan", 0)
            out.Main = servicedata.get("Main", 0)

            return out
        except Exception as e:
            raise ValueError(
                "An error occured while trying to poll all data fields."
                + "Please check your connection"
            ) from e

    def get_energy_cgi(self) -> Dict[str, int]:
        # get energy totals and charge load cycles from CGI
        # "EGrid_AC_DC": 0, "EGrid_DC_AC": 0, "EWr_AC_DC": 0, "EWr_DC_AC": 0,
        # "Chrg_LoadCycles": 0
        result = {}
        results_dict = self._get_cgi_as_dict("/cgi/energy.js", JS_PATTERN_NUMBERS)
        for key, value in results_dict.items():
            result[key] = int(value.replace("[", "").replace("]", ""))
        return result

    def get_ems_cgi(self) -> Dict[str, dict]:
        result = {}

        conf = {
            key.lower(): value
            for key, value in self._get_cgi_as_dict(
                "/cgi/ems_conf.js", JS_PATTERN_ANY
            ).items()
        }
        data = {
            key.lower(): value
            for key, value in self._get_cgi_as_dict(
                "/cgi/ems_data.js", JS_PATTERN_ANY
            ).items()
        }

        for conf_key, value in conf.items():
            data_key = conf_key.replace("conf", "data")
            if data_key not in data:
                continue
            conf_values = ast.literal_eval(value)
            data_values = ast.literal_eval(data[data_key])
            if len(conf_values) != len(data_values):
                continue
            result[conf_key.replace("_conf", "")] = {
                conf_values[i]: data_values[i] for i in range(0, len(conf_values))
            }

        return result

    def get_service_cgi(self) -> Dict[str, int]:
        # get service and maintenance data from CGI
        # "FilterZeit": 0, "Fan": 0, "Main": 0
        result = self._get_cgi_as_dict("/cgi/user_serv.js", JS_PATTERN_NUMBERS)
        return {key: int(value) for key, value in result.items()}

    def get_info_cgi(self) -> Dict[str, str]:
        # get various informations by the cgi/info.js
        return self._get_cgi_as_dict("/cgi/info.js", JS_PATTERN_ANY)

    def _get_cgi_as_dict(self, path: str, pattern: re.Pattern[str]) -> Dict[str, str]:
        result = {}
        try:
            response = self._request_data(path)
            response.raise_for_status()

            results = pattern.findall(response.text)
            result = {resultValue[0]: resultValue[1] for resultValue in results}

        except Exception as e:
            raise ValueError(ERROR_TEMPLATE.format(path)) from e

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
        if results[0] == "2":
            # already logged in
            return True

        login_data = {"user": self.username, "password": self.password}
        response = self.session.post(pass_url, login_data, timeout=3)
        response.raise_for_status()
        return response.status_code == 200
