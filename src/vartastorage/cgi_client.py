import json
import re

import requests

ERROR_TEMPLATE = "An error occured while polling {}. Please check your connection"


class CgiClient:
    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password

        self.session = requests.Session()

    def get_all_data_cgi(self):
        try:
            out = {
                "EGrid_AC_DC": [],
                "EGrid_DC_AC": [],
                "EWr_AC_DC": [],
                "EWr_DC_AC": [],
                "Chrg_LoadCycles": [],
                "FilterZeit": [],
                "Fan": [],
                "Main": [],
            }

            energytotals = self.get_energy_cgi()
            out["EGrid_AC_DC"] = int(energytotals["EGrid_AC_DC"])
            out["EGrid_DC_AC"] = int(energytotals["EGrid_DC_AC"])
            out["EWr_AC_DC"] = int(energytotals["EWr_AC_DC"])
            out["EWr_DC_AC"] = int(energytotals["EWr_DC_AC"])
            out["Chrg_LoadCycles"] = int(energytotals["Chrg_LoadCycles"])

            servicedata = self.get_service_cgi()
            out["FilterZeit"] = int(servicedata["FilterZeit"])
            out["Fan"] = int(servicedata["Fan"])
            out["Main"] = int(servicedata["Main"])

            return out
        except Exception as e:
            raise ValueError(
                "An error occured while trying to poll all data fields."
                + "Please check your connection"
            ) from e

    def get_energy_cgi(self):
        result = {
            "EGrid_AC_DC": 0,
            "EGrid_DC_AC": 0,
            "EWr_AC_DC": 0,
            "EWr_DC_AC": 0,
            "Chrg_LoadCycles": 0,
        }

        # get energy totals and charge load cycles from CGI
        try:
            response = self.request_data("/cgi/energy.js")
            if response.status_code == 200:
                values = re.compile("([a-zA-Z0-9_]+) = ([0-9]+)")
                results = values.findall(response.text)
                for resultValue in results:
                    result[resultValue[0]] = (
                        resultValue[1].replace("]", "").replace("[", "")
                    )

        except Exception as e:
            raise ValueError(ERROR_TEMPLATE.format("energy totals")) from e
        return result

    def get_ems_cgi(self):
        try:
            response = self.request_data("/cgi/ems_data.js")
            data = json.loads(re.findall("EMETER_Data = ([^;]+)", response.text)[0])
            if response.status_code == 200:
                result = {
                    "FNetz": data[0],
                    "U_V_L1": data[1],
                    "U_V_L2": data[2],
                    "U_V_L3": data[3],
                    "Iw_V_L1": data[4],
                    "Iw_V_L2": data[5],
                    "Iw_V_L3": data[6],
                    "Ib_V_L1": data[7],
                    "Ib_V_L2": data[8],
                    "Ib_V_L3": data[9],
                    "Is_V_L1": data[10],
                    "Is_V_L2": data[11],
                    "Is_V_L3": data[12],
                    "Iw_PV_L1": data[13],
                    "Iw_PV_L2": data[14],
                    "Iw_PV_L3": data[15],
                    "Ib_PV_L1": data[16],
                    "Ib_PV_L2": data[17],
                    "Ib_PV_L3": data[18],
                    "Is_PV_L1": data[19],
                    "Is_PV_L2": data[20],
                    "Is_PV_L3": data[21],
                }
        except Exception as e:
            result = {
                "FNetz": 0,
                "U_V_L1": 0,
                "U_V_L2": 0,
                "U_V_L3": 0,
                "Iw_V_L1": 0,
                "Iw_V_L2": 0,
                "Iw_V_L3": 0,
                "Ib_V_L1": 0,
                "Ib_V_L2": 0,
                "Ib_V_L3": 0,
                "Is_V_L1": 0,
                "Is_V_L2": 0,
                "Is_V_L3": 0,
                "Iw_PV_L1": 0,
                "Iw_PV_L2": 0,
                "Iw_PV_L3": 0,
                "Ib_PV_L1": 0,
                "Ib_PV_L2": 0,
                "Ib_PV_L3": 0,
                "Is_PV_L1": 0,
                "Is_PV_L2": 0,
                "Is_PV_L3": 0,
            }
            raise ValueError(ERROR_TEMPLATE.format("ems values")) from e
        return result

    def get_service_cgi(self):
        # get service and maintenance data from CGI
        result = {
            "FilterZeit": 0,
            "Fan": 0,
            "Main": 0,
        }
        try:
            response = self.request_data("/cgi/user_serv.js")
            if response.status_code == 200:
                result = {
                    "FilterZeit": int(response.text.split(";\n")[0].split("= ")[1]),
                    "Fan": int(response.text.split(";\n")[1].split("= ")[1]),
                    "Main": int(response.text.split(";\n")[2].split("= ")[1]),
                }

        except Exception as e:
            raise ValueError(ERROR_TEMPLATE.format("maintainance CGI")) from e
        return result

    def request_data(self, urlEnding):
        try:
            url = "http://" + self.host + urlEnding
            # Check if a password is set
            if self.password:
                # Password is set so we check if already logged in - try 4 times
                for _ in range(4):
                    if self.check_logged_in():
                        return self.session.get(url, timeout=3)
                raise ValueError(
                    "An error occured while polling the maintenance CGI. Couldn't login"
                )
            else:
                return self.session.get(url, timeout=3)
        except Exception as e:
            raise ValueError(ERROR_TEMPLATE) from e

    def check_logged_in(self):
        pass_url = "http://" + self.host + "/cgi/login"
        response = self.session.get(pass_url, timeout=3)
        if response.status_code != 200:
            # Trouble connecting - raise error
            raise ValueError("Login didn't work")
        values = re.compile("userlevel = ([0-9]+)")
        results = values.findall(response.text)
        if results[0] != "2":
            # We are not logged in so we login
            login_data = {"user": self.username, "password": self.password}
            response = self.session.post(pass_url, login_data, timeout=3)
            if response.status_code != 200:
                # We are still not logged in - something went wrong
                raise ValueError("Login didn't work")
            return False
        else:
            return True
