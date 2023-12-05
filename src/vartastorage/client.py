# coding: utf-8

from pymodbus.client.tcp import ModbusTcpClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian
import xml.etree.ElementTree as ET
import requests
import traceback
import sys
import re
import json


class Client(object):
    def __init__(self, modbus_host, modbus_port, password):
        self.modbus_host = modbus_host
        self.modbus_port = modbus_port
        self.password = password
        self.modbus_client = ModbusTcpClient(self.modbus_host, self.modbus_port)

        self.session = requests.Session()

    def connect(self):
        return self.modbus_client.connect()

    def disconnect(self):
        return self.modbus_client.close()

    def check_if_socket_open(self):
        return self.modbus_client.is_socket_open()

    def get_all_data(self):
        try:
            out = {
                "soc": [],
                "grid_power": [],
                "state": [],
                "active_power": [],
                "apparent_power": [],
                "error_code": [],
                "total_charged_energy": [],
                "serial": [],
                "EGrid_AC_DC": [],
                "EGrid_DC_AC": [],
                "EWr_AC_DC": [],
                "EWr_DC_AC": [],
                "Chrg_LoadCycles": [],
            }
            out["soc"] = self.get_soc()
            out["grid_power"] = self.get_grid_power()
            out["state"] = self.get_state()
            out["active_power"] = self.get_active_power()
            out["apparent_power"] = self.get_apparent_power()
            out["error_code"] = self.get_error_code()
            out["total_charged_energy"] = self.get_total_charged_energy()
            out["serial"] = self.get_serial()

            energytotals = self.get_energy_cgi()
            out["EGrid_AC_DC"] = energytotals["EGrid_AC_DC"]
            out["EGrid_DC_AC"] = energytotals["EGrid_DC_AC"]
            out["EWr_AC_DC"] = energytotals["EWr_AC_DC"]
            out["Chrg_LoadCycles"] = energytotals["Chrg_LoadCycles"]

            return out
        except Exception as e:
            raise ValueError("An error occured while trying to poll all data fields. Please check your connection")

    def get_grid_power(self):
        try:
            self.connect()
            rr = self.modbus_client.read_holding_registers(1078, 1, slave=255)

            if not rr.isError():
                res = BinaryPayloadDecoder.fromRegisters(
                    rr.registers, Endian.BIG, Endian.LITTLE
                ).decode_16bit_int()

                self.modbus_client.close()
                return res

        except Exception as e:
            raise ValueError("An error occured while polling grid power. Please check your connection")

    def get_soc(self):
        try:
            self.connect()
            rr = self.modbus_client.read_holding_registers(1068, 1, slave=255)

            if not rr.isError():
                res = BinaryPayloadDecoder.fromRegisters(
                    rr.registers, Endian.BIG, Endian.LITTLE
                ).decode_16bit_uint()

                self.modbus_client.close()
                return res

        except Exception as e:
            raise ValueError("An error occured while polling state of charge. Please check your connection")

    def get_state(self):
        try:
            self.connect()
            rr = self.modbus_client.read_holding_registers(1065, 1, slave=255)

            if not rr.isError():
                res = BinaryPayloadDecoder.fromRegisters(
                    rr.registers, Endian.BIG, Endian.LITTLE
                ).decode_16bit_uint()

                self.modbus_client.close()
                return res

        except Exception as e:
            raise ValueError("An error occured while polling the device state. Please check your connection")

    def get_active_power(self):
        try:
            self.connect()
            rr = self.modbus_client.read_holding_registers(1066, 1, slave=255)

            if not rr.isError():
                res = BinaryPayloadDecoder.fromRegisters(
                    rr.registers, Endian.BIG, Endian.LITTLE
                ).decode_16bit_int()

                self.modbus_client.close()
                return res

        except Exception as e:
            raise ValueError("An error occured while polling active power. Please check your connection")

    def get_apparent_power(self):
        try:
            self.connect()
            rr = self.modbus_client.read_holding_registers(1067, 1, slave=255)

            if not rr.isError():
                res = BinaryPayloadDecoder.fromRegisters(
                    rr.registers, Endian.BIG, Endian.LITTLE
                ).decode_16bit_int()

                self.modbus_client.close()
                return res

        except Exception as e:
            raise ValueError("An error occured while polling apparent power. Please check your connection")

    def get_error_code(self):
        try:
            self.connect()
            rr = self.modbus_client.read_holding_registers(1072, 1, slave=255)

            if not rr.isError():
                res = BinaryPayloadDecoder.fromRegisters(
                    rr.registers, Endian.BIG, Endian.LITTLE
                ).decode_16bit_uint()

                self.modbus_client.close()
                return res

        except Exception as e:
            raise ValueError("An error occured while polling the error code. Please check your connection")

    def get_total_charged_energy(self):
        try:
            self.connect()
            rr_low = self.modbus_client.read_holding_registers(1069, 1, slave=255)
            if not rr_low.isError():
                res_low = BinaryPayloadDecoder.fromRegisters(
                    rr_low.registers, Endian.BIG, Endian.LITTLE
                ).decode_16bit_uint()

            rr_high = self.modbus_client.read_holding_registers(1070, 1, slave=255)
            if not rr_high.isError():
                res_high = BinaryPayloadDecoder.fromRegisters(
                    rr_high.registers, Endian.BIG, Endian.LITTLE
                ).decode_16bit_uint()

            self.modbus_client.close()

            if not rr_low.isError() and not rr_high.isError():
                res = ((res_high << 16) | (res_low & 0xFFFF)) / 1000
                return res

        except Exception as e:
            raise ValueError("An error occured while polling the total charged energy. Please check your connection")

    def get_serial(self):
        try:
            response = self.request_data("/cgi/ems_data.xml")
            if response.status_code == 200:
                result = ET.fromstring(response.text)
                result = result.get("id")
        except Exception as e:
            result = 0
            raise ValueError("An error occured while polling the serial number. Please check your connection")
        return result

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
                    result[resultValue[0]] = resultValue[1].replace("]", "").replace("[", "")

        except Exception as e:
            raise ValueError("An error occured while polling the energy totals. Please check your connection")
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
            raise ValueError("An error occured while polling the ems values. Please check your connection")
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
                values = re.compile("([a-zA-Z0-9_]+) = ([0-9]+)")
                results = values.findall(response.text)
                for resultValue in results:
                    result[resultValue[0]] = resultValue[1]

        except Exception as e:
            raise ValueError("An error occured while polling the maintenance CGI. Please check your connection")
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
                raise ValueError("An error occured while polling the maintenance CGI. Couldn't login")
            else:
                return self.session.get(url, timeout=3)
        except Exception as e:
            raise ValueError("An error occured while polling the maintenance CGI. Please check your connection")

    def check_logged_in(self):
        pass_url = "http://" + self.modbus_host + "/cgi/login"
        response = self.session.get(pass_url, timeout=3)
        if response.status_code != 200:
            # Trouble connecting - raise error
                raise ValueError("An error occured while polling the maintenance CGI. Login didn't work")
        values = re.compile("userlevel = ([0-9]+)")
        results = values.findall(response.text)
        if results[0] != "2":
            # We are not logged in so we login
            login_data = {"user": "user1", "password": self.password}
            response = self.session.post(pass_url, login_data, timeout=3)
            if response.status_code != 200:
                # We are still not logged in - something went wrong
                raise ValueError("An error occured while polling the maintenance CGI. Login didn't work")
            return False
        else:
            return True