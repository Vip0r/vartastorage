from dataclasses import dataclass
from time import time

from pymodbus.client.tcp import ModbusTcpClient
from pymodbus.exceptions import ModbusException

ERROR_TEMPLATE = (
    "An error occurred while polling address {}. "
    + "This might be an issue with your device."
)

CACHE_TIME = 900  # 15 minutes


@dataclass
class RawData:
    soc: int
    grid_power: int
    state: int
    active_power: int
    apparent_power: int
    error_code: int
    total_charged_energy: int
    number_modules: int
    installed_capacity: int
    serial: str
    table_version: int
    software_version_ems: str
    software_version_ens: str
    software_version_inverter: str


@dataclass
class CacheData:
    timestamp_cache: int = 0
    serial: str = ""
    table_version: int = 0
    software_version_ems: str = ""
    software_version_ens: str = ""
    software_version_inverter: str = ""

    def set_data(
        self,
        serial: str,
        table_version: int,
        software_version_ems: str,
        software_version_ens: str,
        software_version_inverter: str,
    ) -> None:
        self.timestamp_cache = int(time())
        self.serial = serial
        self.table_version = table_version
        self.software_version_ems = software_version_ems
        self.software_version_ens = software_version_ens
        self.software_version_inverter = software_version_inverter


class ModbusClient:
    def __init__(self, modbus_host: str, modbus_port: int, device_id: int) -> None:
        self._device_id = device_id
        self.modbus_host = modbus_host
        self.modbus_port = modbus_port
        self._modbus_client = ModbusTcpClient(
            host=self.modbus_host, port=self.modbus_port
        )

        self._cache = CacheData()

    def connect(self) -> bool:
        return self._modbus_client.connect()

    def disconnect(self) -> None:
        self._modbus_client.close()

    def is_connected(self) -> bool:
        return self._modbus_client.is_socket_open()

    def get_all_data_modbus(self) -> RawData:
        self.update_cache()
        out = RawData(
            soc=self.get_soc(),
            grid_power=self.get_grid_power(),
            state=self.get_state(),
            active_power=self.get_active_power(),
            apparent_power=self.get_apparent_power(),
            error_code=self.get_error_code(),
            number_modules=self.get_bm_installed(),
            installed_capacity=self.get_installed_capacity(),
            total_charged_energy=self.get_total_charged_energy(),
            serial=self._cache.serial,
            table_version=self._cache.table_version,
            software_version_ems=self._cache.software_version_ems,
            software_version_ens=self._cache.software_version_ens,
            software_version_inverter=self._cache.software_version_inverter,
        )
        return out

    def update_cache(self) -> None:
        if int(time()) - self._cache.timestamp_cache < CACHE_TIME:
            # cache is still relevant
            return

        self._cache.set_data(
            serial=self.get_serial(),
            table_version=self.get_table_version(),
            software_version_ems=self.get_software_version_ems(),
            software_version_ens=self.get_software_version_ens(),
            software_version_inverter=self.get_software_version_inverter(),
        )

    def get_software_version_ems(self) -> str:
        registers = self._get_value_modbus(1000, 17)
        result = ModbusTcpClient.convert_from_registers(
            registers, data_type=ModbusTcpClient.DATATYPE.STRING, word_order="big"
        )
        # Decode using UTF-16 little-endian
        return self._clean_string(result)

    def get_software_version_ens(self) -> str:
        registers = self._get_value_modbus(1017, 17)
        result = ModbusTcpClient.convert_from_registers(
            registers, data_type=ModbusTcpClient.DATATYPE.STRING, word_order="big"
        )
        # Decode using UTF-16 little-endian
        return self._clean_string(result)

    def get_software_version_inverter(self) -> str:
        registers = self._get_value_modbus(1034, 17)
        result = ModbusTcpClient.convert_from_registers(
            registers, data_type=ModbusTcpClient.DATATYPE.STRING, word_order="big"
        )
        # Decode using UTF-16 little-endian
        return self._clean_string(result)

    def get_table_version(self) -> int:
        registers = self._get_value_modbus(1051, 1)
        result = ModbusTcpClient.convert_from_registers(
            registers, data_type=ModbusTcpClient.DATATYPE.UINT16, word_order="big"
        )
        return self._convert_value_to_int(result)

    def get_serial(self) -> str:
        # Retrieves the Serial Number of the device
        # Supported on VARTA element, pulse, pulse neo, link and flex storage devices

        registers = self._get_value_modbus(1054, 10)
        result = ModbusTcpClient.convert_from_registers(
            registers, data_type=ModbusTcpClient.DATATYPE.STRING, word_order="big"
        )
        # Extract only the ASCII-readable characters (digits in this case)
        return self._clean_string(result)

    def get_bm_installed(self) -> int:
        # Retrieves the number of battery modules installed
        # Supported on VARTA element, pulse, pulse neo, link and flex storage devices

        registers = self._get_value_modbus(1064, 1)
        result = ModbusTcpClient.convert_from_registers(
            registers, data_type=ModbusTcpClient.DATATYPE.UINT16, word_order="big"
        )
        return self._convert_value_to_int(result)

    def get_state(self) -> int:
        # Retrieves the state of the device
        #  # "BUSY" (e.g. during startup) = 0/ "RUN" (ready to charge / discharge) = 1/
        # "CHARGE" = 2/ "DISCHARGE" = 3/ "STANDBY" = 4 /"ERROR" = 5 /
        # "PASSIVE" (service) = 6/ "ISLANDING" = 7
        # Supported on VARTA element, pulse, pulse neo, link and flex storage devices

        registers = self._get_value_modbus(1065, 1)
        result = ModbusTcpClient.convert_from_registers(
            registers, data_type=ModbusTcpClient.DATATYPE.UINT16, word_order="big"
        )
        return self._convert_value_to_int(result)

    def get_active_power(self) -> int:
        # Active Power measured at the internal inverter. Positive = Charge,
        # Negative = Discharge
        # Supported on VARTA element, pulse, pulse neo, link and flex storage devices

        registers = self._get_value_modbus(1066, 1)
        result = ModbusTcpClient.convert_from_registers(
            registers, data_type=ModbusTcpClient.DATATYPE.INT16, word_order="big"
        )
        return self._convert_value_to_int(result)

    def get_apparent_power(self) -> int:
        # Apparent Power measured at the internal inverter. Positive = Charge,
        # Negative = Discharge
        # Supported on VARTA element, pulse, pulse neo, link and flex storage devices

        registers = self._get_value_modbus(1067, 1)
        result = ModbusTcpClient.convert_from_registers(
            registers, data_type=ModbusTcpClient.DATATYPE.INT16, word_order="big"
        )
        return self._convert_value_to_int(result)

    def get_soc(self) -> int:
        # Current State of Charge of the Battery Power
        # Supported on VARTA element, pulse, pulse neo, link and flex storage devices

        registers = self._get_value_modbus(1068, 1)
        result = ModbusTcpClient.convert_from_registers(
            registers, data_type=ModbusTcpClient.DATATYPE.UINT16, word_order="big"
        )
        return self._convert_value_to_int(result)

    def get_total_charged_energy(self) -> int:
        # Total charged energy
        # Supported on VARTA element, pulse, pulse neo, link and flex storage devices

        reg_low = self._get_value_modbus(1069, 1)
        reg_high = self._get_value_modbus(1070, 1)

        res_low = ModbusTcpClient.convert_from_registers(
            reg_low, data_type=ModbusTcpClient.DATATYPE.UINT16, word_order="big"
        )
        res_high = ModbusTcpClient.convert_from_registers(
            reg_high, data_type=ModbusTcpClient.DATATYPE.UINT16, word_order="big"
        )

        res_low_int = self._convert_value_to_int(res_low)
        res_high_int = self._convert_value_to_int(res_high)

        result = (res_high_int << 16) | (res_low_int & 0xFFFF)
        return int(result / 1000)

    def get_installed_capacity(self) -> int:
        # Retrieves the total installed capacity in the device
        # Supported on VARTA element, pulse, pulse neo, link and flex storage devices

        registers = self._get_value_modbus(1071, 1)
        result = ModbusTcpClient.convert_from_registers(
            registers, data_type=ModbusTcpClient.DATATYPE.UINT16, word_order="big"
        )
        # Installed capacity has to be multiplied by 10
        return self._convert_value_to_int(result) * 10

    def get_error_code(self) -> int:
        registers = self._get_value_modbus(1072, 1)
        result = ModbusTcpClient.convert_from_registers(
            registers, data_type=ModbusTcpClient.DATATYPE.UINT16, word_order="big"
        )
        return self._convert_value_to_int(result)

    def get_grid_power(self) -> int:
        # Retrieves the current grid power measured at household grid connection point
        # Supported on VARTA element, pulse, pulse neo, link and flex storage devices

        registers = self._get_value_modbus(1078, 1)
        result = ModbusTcpClient.convert_from_registers(
            registers, data_type=ModbusTcpClient.DATATYPE.INT16, word_order="big"
        )
        return self._convert_value_to_int(result)

    def _get_value_modbus(self, address, count) -> list:
        if not self._modbus_client.is_socket_open():
            self._modbus_client.connect()

        try:
            rr = self._modbus_client.read_holding_registers(
                address=address, count=count, device_id=self._device_id
            )
        except ModbusException as exc:
            raise ValueError(ERROR_TEMPLATE.format(address)) from exc

        if rr.isError():
            raise ValueError(ERROR_TEMPLATE.format(address))

        return rr.registers

    @staticmethod
    def _clean_string(input_bytes) -> str:
        # I know this is super wierd. But i have no idea whats here going on in the
        # pymodbus library and i have to use this function to reformat the string
        # correctly
        r = "".join(c for c in input_bytes if c.isprintable())
        return r

    @staticmethod
    def _convert_value_to_int(value: int | float | str | list) -> int:
        if isinstance(value, list):
            # if value is a list, return the first element or 0 if the list is empty
            return int(value[0]) if value else 0
        return int(value)
