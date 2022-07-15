# coding: utf-8

from pymodbus.client.sync import ModbusTcpClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian
import xml.etree.ElementTree as ET
import requests
import traceback
import sys


class Client(object):
    def __init__(self, modbus_host, modbus_port):

        self.modbus_host = modbus_host
        self.modbus_port = modbus_port
        self.modbus_client = ModbusTcpClient(self.modbus_host, self.modbus_port)

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
            out["EWr_DC_AC"] = energytotals["EWr_DC_AC"]
            out["Chrg_LoadCycles"] = energytotals["Chrg_LoadCycles"]

            return out
        except Exception as e:
            raise ValueError("An error occured while trying to poll all data fields. Please check your connection")

    def get_grid_power(self):
        try:
            self.connect()
            rr = self.modbus_client.read_holding_registers(1078, 1, unit=255)

            if not rr.isError():
                res = BinaryPayloadDecoder.fromRegisters(
                    rr.registers, Endian.Big, Endian.Little
                ).decode_16bit_int()

                self.modbus_client.close()
                return res

        except Exception as e:
            raise ValueError("An error occured while polling grid power. Please check your connection")

    def get_soc(self):
        try:
            self.connect()
            rr = self.modbus_client.read_holding_registers(1068, 1, unit=255)

            if not rr.isError():
                res = BinaryPayloadDecoder.fromRegisters(
                    rr.registers, Endian.Big, Endian.Little
                ).decode_16bit_uint()

                self.modbus_client.close()
                return res

        except Exception as e:
            raise ValueError("An error occured while polling state of charge. Please check your connection")

    def get_state(self):
        try:
            self.connect()
            rr = self.modbus_client.read_holding_registers(1065, 1, unit=255)

            if not rr.isError():
                res = BinaryPayloadDecoder.fromRegisters(
                    rr.registers, Endian.Big, Endian.Little
                ).decode_16bit_uint()

                self.modbus_client.close()
                return res

        except Exception as e:
            raise ValueError("An error occured while polling the device state. Please check your connection")

    def get_active_power(self):
        try:
            self.connect()
            rr = self.modbus_client.read_holding_registers(1066, 1, unit=255)

            if not rr.isError():
                res = BinaryPayloadDecoder.fromRegisters(
                    rr.registers, Endian.Big, Endian.Little
                ).decode_16bit_int()

                self.modbus_client.close()
                return res

        except Exception as e:
            raise ValueError("An error occured while polling active power. Please check your connection")

    def get_apparent_power(self):
        try:
            self.connect()
            rr = self.modbus_client.read_holding_registers(1067, 1, unit=255)

            if not rr.isError():
                res = BinaryPayloadDecoder.fromRegisters(
                    rr.registers, Endian.Big, Endian.Little
                ).decode_16bit_int()

                self.modbus_client.close()
                return res

        except Exception as e:
            raise ValueError("An error occured while polling apparent power. Please check your connection")

    def get_error_code(self):
        try:
            self.connect()
            rr = self.modbus_client.read_holding_registers(1072, 1, unit=255)

            if not rr.isError():
                res = BinaryPayloadDecoder.fromRegisters(
                    rr.registers, Endian.Big, Endian.Little
                ).decode_16bit_uint()

                self.modbus_client.close()
                return res

        except Exception as e:
            raise ValueError("An error occured while polling the error code. Please check your connection")

    def get_total_charged_energy(self):
        try:
            self.connect()
            rr_low = self.modbus_client.read_holding_registers(1069, 1, unit=255)
            if not rr_low.isError():
                res_low = BinaryPayloadDecoder.fromRegisters(
                    rr_low.registers, Endian.Big, Endian.Little
                ).decode_16bit_uint()

            rr_high = self.modbus_client.read_holding_registers(1070, 1, unit=255)
            if not rr_high.isError():
                res_high = BinaryPayloadDecoder.fromRegisters(
                    rr_high.registers, Endian.Big, Endian.Little
                ).decode_16bit_uint()

            self.modbus_client.close()

            if not rr_low.isError() and not rr_high.isError():
                res = ((res_high << 16) | (res_low & 0xFFFF)) / 1000
                return res

        except Exception as e:
            raise ValueError("An error occured while polling the total charged energy. Please check your connection")

    def get_serial(self):
        url = "http://" + self.modbus_host + "/cgi/ems_data.xml"
        try:
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                result = ET.fromstring(response.text)
                return result.get("id")
        except Exception as e:
            raise ValueError("An error occured while polling the serial number. Please check your connection") 

    def get_energy_cgi(self):
        #get energy totals and charge load cycles from CGI
        url = "http://" + self.modbus_host + "/cgi/energy.js"
        try:
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                #asdasd
                result = {
                "EGrid_AC_DC": response.text.split(';\n')[0].split('= ')[1],
                "EGrid_DC_AC": response.text.split(';\n')[1].split('= ')[1],
                "EWr_AC_DC": response.text.split(';\n')[2].split('= ')[1],
                "EWr_DC_AC": response.text.split(';\n')[3].split('= ')[1],
                "Chrg_LoadCycles": response.text.split(';\n')[4].split('= ')[1].replace("]","").replace("[","")
                }
                return result
        except Exception as e:
            raise ValueError("An error occured while polling the energy totals. Please check your connection") 

    def get_service_cgi(self):
        #get service and maintenance data from CGI
        url = "http://" + self.modbus_host + "/cgi/user_serv.js"
        try:
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                #asdasd
                result = {
                "FilterZeit": response.text.split(';\n')[0].split('= ')[1],
                "Fan": response.text.split(';\n')[1].split('= ')[1],
                "Main": response.text.split(';\n')[2].split('= ')[1],
                }
                return result
        except Exception as e:
            raise ValueError("An error occured while polling the maintenance CGI. Please check your connection") 
    