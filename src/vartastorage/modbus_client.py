from pymodbus.client.tcp import ModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.exceptions import ModbusException
from pymodbus.payload import BinaryPayloadDecoder

ERROR_STRING = (
    "An error occured while trying to poll all data fields."
    + "Please check your connection"
)
ERROR_TEMPLATE = (
    "An error occured while polling adress {}."
    + "This might be an issue with your device."
)


class ModbusClient:
    def __init__(self, modbus_host, modbus_port):
        self._slave = 255

        self.modbus_host = modbus_host
        self.modbus_port = modbus_port
        self.modbus_client = ModbusTcpClient(self.modbus_host, self.modbus_port)

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
            raise ValueError(ERROR_STRING) from e

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
        # pymodbus library and i have to use this function to reformat the string
        # correctly
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
        # "CHARGE" = 2/ "DISCHARGE" = 3/ "STANDBY" = 4 /"ERROR" = 5 /
        # "PASSIVE" (service) = 6/ "ISLANDING" = 7
        # Supported on VARTA element, pulse, pulse neo, link and flex storage devices

        registers = self._get_value_modbus(1065, 1)
        result = BinaryPayloadDecoder.fromRegisters(
            registers, Endian.BIG, Endian.LITTLE
        ).decode_16bit_uint()
        return result

    def get_active_power_modbus(self):
        # Active Power measured at the internal inverter. Positive = Charge,
        # Negative = Discharge
        # Supported on VARTA element, pulse, pulse neo, link and flex storage devices

        registers = self._get_value_modbus(1066, 1)
        result = BinaryPayloadDecoder.fromRegisters(
            registers, Endian.BIG, Endian.LITTLE
        ).decode_16bit_int()
        return result

    def get_apparent_power_modbus(self):
        # Apparent Power measured at the internal inverter. Positive = Charge,
        # Negative = Discharge
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
            raise ValueError(ERROR_TEMPLATE.format(address)) from exc

        if rr.isError():
            raise ValueError(ERROR_TEMPLATE.format(address))

        return rr.registers
