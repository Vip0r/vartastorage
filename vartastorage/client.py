# coding: utf-8

from pymodbus.client.sync import ModbusTcpClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian


class Client(object):
    def __init__(self, modbus_host, modbus_port):

        self.modbus_host = modbus_host
        self.modbus_port = modbus_port

    def connect(self):
        self.modbus_client = ModbusTcpClient(self.modbus_host, self.modbus_port)
        if self.modbus_client.connect():
            return True

        else:
            raise ValueError(
                "Connection to modbus server was not sucessful, please review your configuration"
            )

    def get_all_data(self):
        out = {
            "grid_power": [],
            "soc": [],
            "state": [],
            "active_power": [],
            "apparent_power": [],
            "production_power": [],
            "total_production_power": [],
            "error_code": [],
            "total_charged_energy": []
        }
        try:
            out["grid_power"] = self.get_grid_power()
            out["soc"] = self.get_soc()
            out["state"] = self.get_state()
            out["active_power"] = self.get_active_power()
            out["apparent_power"] = self.get_apparent_power()
            out["production_power"] = self.get_production_power()
            out["total_production_power"] = self.get_total_production_power()
            out["error_code"] = self.get_error_code()
            out["total_charged_energy"] = self.get_total_charged_energy()
        except:
            pass

        return out

    def get_grid_power(self):
        try:
            self.connect()
            rr = self.modbus_client.read_holding_registers(1078, 1, unit=255)

            if not rr.isError():
                res = BinaryPayloadDecoder.fromRegisters(
                    rr.registers, Endian.Big, Endian.Little
                ).decode_16bit_int()

        except:
            pass

        self.modbus_client.close()
        return res

    def get_soc(self):
        try:
            self.connect()
            rr = self.modbus_client.read_holding_registers(1068, 1, unit=255)

            if not rr.isError():
                res = BinaryPayloadDecoder.fromRegisters(
                    rr.registers, Endian.Big, Endian.Little
                ).decode_16bit_uint()

        except:
            pass

        self.modbus_client.close()
        return res

    def get_state(self):
        try:
            self.connect()
            rr = self.modbus_client.read_holding_registers(1065, 1, unit=255)

            if not rr.isError():
                res = BinaryPayloadDecoder.fromRegisters(
                    rr.registers, Endian.Big, Endian.Little
                ).decode_16bit_uint()

        except:
            pass

        self.modbus_client.close()
        return res

    def get_active_power(self):
        try:
            self.connect()
            rr = self.modbus_client.read_holding_registers(1066, 1, unit=255)

            if not rr.isError():
                res = BinaryPayloadDecoder.fromRegisters(
                    rr.registers, Endian.Big, Endian.Little
                ).decode_16bit_int()

        except:
            pass

        self.modbus_client.close()
        return res

    def get_apparent_power(self):
        try:
            self.connect()
            rr = self.modbus_client.read_holding_registers(1067, 1, unit=255)

            if not rr.isError():
                res = BinaryPayloadDecoder.fromRegisters(
                    rr.registers, Endian.Big, Endian.Little
                ).decode_16bit_int()

        except:
            pass

        self.modbus_client.close()
        return res

    def get_production_power(self):
        try:
            self.connect()
            rr = self.modbus_client.read_holding_registers(1100, 1, unit=255)

            if not rr.isError():
                res = BinaryPayloadDecoder.fromRegisters(
                    rr.registers, Endian.Big, Endian.Little
                ).decode_16bit_uint()

        except:
            pass

        self.modbus_client.close()
        return res

    def get_total_production_power(self):
        try:
            self.connect()
            rr = self.modbus_client.read_holding_registers(1101, 1, unit=255)

            if not rr.isError():
                res = BinaryPayloadDecoder.fromRegisters(
                    rr.registers, Endian.Big, Endian.Little
                ).decode_16bit_float()

        except:
            pass

        self.modbus_client.close()
        return res

    def get_error_code(self):
        try:
            self.connect()
            rr = self.modbus_client.read_holding_registers(1072, 1, unit=255)

            if not rr.isError():
                res = BinaryPayloadDecoder.fromRegisters(
                    rr.registers, Endian.Big, Endian.Little
                ).decode_16bit_uint()

        except:
            pass

        self.modbus_client.close()
        return res

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
        except:
            pass

        self.modbus_client.close()

        res = ((res_high << 16) | (res_low & 0xFFFF))/1000

        return res