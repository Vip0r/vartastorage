# coding: utf-8

from pymodbus.client.tcp import ModbusTcpClient
from pymodbus.exceptions import ModbusException
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian
import xml.etree.ElementTree as ET
import requests
import re
import json


class Client(object):
    def __init__(self, modbus_host, modbus_port, username, password):
        self._slave = 255

        self.modbus_host = modbus_host
        self.modbus_port = modbus_port
        self.modbus_client = ModbusTcpClient(self.modbus_host, self.modbus_port)

        self.username = username
        self.password = password

        self.session = requests.Session()

    def connect(self):
        return self.modbus_client.connect()

    def disconnect(self):
        return self.modbus_client.close()

    def check_if_socket_open(self):
        return self.modbus_client.is_socket_open()

    def get_all_data_modbus(self):
        try:
            out = {
                "soc": [],
                "grid_power": [],
                "state": [],
                "active_power": [],
                "apparent_power": [],
                "error_code": [],
                "total_charged_energy": [],
                "number_modules": [],
                "installed_capacity": [],
                "serial": [],
            }
            out["soc"] = self.get_soc_modbus()
            out["grid_power"] = self.get_grid_power_modbus()
            out["state"] = self.get_state_modbus()
            out["active_power"] = self.get_active_power_modbus()
            out["apparent_power"] = self.get_apparent_power_modbus()
            out["error_code"] = self.get_error_code_modbus()
            out["number_modules"] = self.get_bm_modbus()
            out["installed_capacity"] = self.get_installed_capacity_modbus()
            out["total_charged_energy"] = self.get_total_charged_energy_modbus()
            out["serial"] = self.get_serial_modbus()

            return out
        except Exception as e:
            raise ValueError(
                "An error occured while trying to poll all data fields. Please check your connection"
            ) from e

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
                "An error occured while trying to poll all data fields. Please check your connection"
            )

    def get_serial_modbus(self):
        # Retrieves the Serial Number of the device
        # Supported on VARTA element, pulse, pulse neo, link and flex storage devices

        registers = self._get_value_modbus(1054, 10)

        result = (
            BinaryPayloadDecoder.fromRegisters(registers, Endian.BIG, Endian.BIG)
            .decode_string(18)
            .decode()
        )

        # I know this is super wierd. But i have no idea whats here going on in the
        # pymodbus library and i have to use this function to reformat the string correctly
        chars = [x for x in result]
        result_string = "".join(chars[1::2])
        res = result_string

        return res

    def get_bm_modbus(self):
        # Retrieves the number of battery modules installed
        # Supported on VARTA element, pulse, pulse neo, link and flex storage devices

        registers = self._get_value_modbus(1064, 1)
        result = BinaryPayloadDecoder.fromRegisters(
            registers, Endian.BIG, Endian.LITTLE
        ).decode_16bit_uint()
        return result

    def get_state_modbus(self):
        # Retrieves the state of the device
        #  # "BUSY" (e.g. during startup) = 0/ "RUN" (ready to charge / discharge) = 1/
        # "CHARGE" = 2/ "DISCHARGE" = 3/ "STANDBY" = 4 /"ERROR" = 5 / "PASSIVE" (service) = 6/ "ISLANDING" = 7
        # Supported on VARTA element, pulse, pulse neo, link and flex storage devices

        registers = self._get_value_modbus(1065, 1)
        result = BinaryPayloadDecoder.fromRegisters(
            registers, Endian.BIG, Endian.LITTLE
        ).decode_16bit_uint()
        return result

    def get_active_power_modbus(self):
        # Active Power measured at the internal inverter. Positive = Charge, Negative = Discharge
        # Supported on VARTA element, pulse, pulse neo, link and flex storage devices

        registers = self._get_value_modbus(1066, 1)
        result = BinaryPayloadDecoder.fromRegisters(
            registers, Endian.BIG, Endian.LITTLE
        ).decode_16bit_int()
        return result

    def get_apparent_power_modbus(self):
        # Apparent Power measured at the internal inverter. Positive = Charge, Negative = Discharge
        # Supported on VARTA element, pulse, pulse neo, link and flex storage devices

        registers = self._get_value_modbus(1067, 1)
        result = BinaryPayloadDecoder.fromRegisters(
            registers, Endian.BIG, Endian.LITTLE
        ).decode_16bit_int()
        return result

    def get_soc_modbus(self):
        # Current State of Charge of the Battery Power
        # Supported on VARTA element, pulse, pulse neo, link and flex storage devices

        registers = self._get_value_modbus(1068, 1)
        result = BinaryPayloadDecoder.fromRegisters(
            registers, Endian.BIG, Endian.LITTLE
        ).decode_16bit_uint()
        return result

    def get_total_charged_energy_modbus(self):
        # Total charged energy
        # Supported on VARTA element, pulse, pulse neo, link and flex storage devices

        reg_low = self._get_value_modbus(1069, 1)
        reg_high = self._get_value_modbus(1070, 1)

        res_low = BinaryPayloadDecoder.fromRegisters(
            reg_low, Endian.BIG, Endian.LITTLE
        ).decode_16bit_uint()

        res_high = BinaryPayloadDecoder.fromRegisters(
            reg_high, Endian.BIG, Endian.LITTLE
        ).decode_16bit_uint()

        res = ((res_high << 16) | (res_low & 0xFFFF)) / 1000
        return res

    def get_installed_capacity_modbus(self):
        # Retrieves the total installed capacity in the device
        # Supported on VARTA element, pulse, pulse neo, link and flex storage devices

        registers = self._get_value_modbus(1071, 1)
        result = BinaryPayloadDecoder.fromRegisters(
            registers, Endian.BIG, Endian.LITTLE
        ).decode_16bit_uint()
        return result

    def get_error_code_modbus(self):

        registers = self._get_value_modbus(1072, 1)
        result = BinaryPayloadDecoder.fromRegisters(
            registers, Endian.BIG, Endian.LITTLE
        ).decode_16bit_uint()
        return result

    def get_grid_power_modbus(self):
        # Retrieves the current grid power measured at household grid connection point
        # Supported on VARTA element, pulse, pulse neo, link and flex storage devices

        registers = self._get_value_modbus(1078, 1)
        result = BinaryPayloadDecoder.fromRegisters(
            registers, Endian.BIG, Endian.LITTLE
        ).decode_16bit_int()
        return result

    def _get_value_modbus(self, address, count):
        if not self.modbus_client.is_socket_open():
            self.modbus_client.connect()

        try:
            rr = self.modbus_client.read_holding_registers(
                address, count, slave=self._slave
            )
        except ModbusException as exc:
            raise ValueError(
                f"An error occured while polling adress {address}. Please check your connection."
            ) from exc

        if rr.isError():
            raise ValueError(
                f"An error occured while polling adress {address}. This might be an issue with your device."
            )

        return rr.registers

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
            raise ValueError(
                "An error occured while polling the energy totals. Please check your connection"
            )
        return result

    def get_ems_cgi(self):
        url = "http://" + self.modbus_host + "/cgi/ems_data.js"
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
            raise ValueError(
                "An error occured while polling the ems values. Please check your connection"
            )
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
            raise ValueError(
                "An error occured while polling the maintenance CGI. Please check your connection"
            )
        return result

    def request_data(self, urlEnding):
        try:
            url = "http://" + self.modbus_host + urlEnding
            # Check if a password is set
            if self.password:
                # Password is set so we check if we are already logged in - we try 4 times
                for i in range(4):
                    if self.check_logged_in():
                        return self.session.get(url, timeout=3)
                raise ValueError(
                    "An error occured while polling the maintenance CGI. Couldn't login"
                )
            else:
                return self.session.get(url, timeout=3)
        except Exception as e:
            raise ValueError(
                "An error occured while polling the maintenance CGI. Please check your connection"
            )

    def check_logged_in(self):
        pass_url = "http://" + self.modbus_host + "/cgi/login"
        response = self.session.get(pass_url, timeout=3)
        if response.status_code != 200:
            # Trouble connecting - raise error
            raise ValueError(
                "An error occured while polling the maintenance CGI. Login didn't work"
            )
        values = re.compile("userlevel = ([0-9]+)")
        results = values.findall(response.text)
        if results[0] != "2":
            # We are not logged in so we login
            login_data = {"user": self.username, "password": self.password}
            response = self.session.post(pass_url, login_data, timeout=3)
            if response.status_code != 200:
                # We are still not logged in - something went wrong
                raise ValueError(
                    "An error occured while polling the maintenance CGI. Login didn't work"
                )
            return False
        else:
            return True
