from dataclasses import dataclass
from typing import Tuple

from vartastorage.cgi_client import CgiClient
from vartastorage.modbus_client import ModbusClient

CGI_ERR = "The CgiClient is not initialized. Did you set cgi=False?"


@dataclass
class VartaStorageData:
    # raw data
    soc: int = 0
    grid_power: int = 0
    state: int = 0
    active_power: int = 0
    apparent_power: int = 0
    error_code: int = 0
    total_charged_energy: int = 0
    number_modules: int = 0
    installed_capacity: int = 0
    serial: str = ""

    # interpretations
    state_text: str = ""
    to_grid_power: int = 0
    from_grid_power: int = 0
    charge_power: int = 0
    discharge_power: int = 0


class VartaStorage:
    def __init__(
        self, modbus_host, modbus_port, cgi=True, username=None, password=None
    ):
        # connect to modbus server
        self.modbus_client = ModbusClient(modbus_host, modbus_port)

        # connect to cgi
        if cgi:
            self.cgi_client = CgiClient(modbus_host, username, password)

    def get_all_data_modbus(self):
        out = VartaStorageData
        res = self.get_raw_data_modbus()

        calc_grid_power = self._calculate_to_from_grid(res.grid_power)
        calc_charge_power = self._calculate_charge_discharge(res.active_power)

        out.soc = res.soc
        out.grid_power = res.grid_power
        out.to_grid_power = calc_grid_power[0]
        out.from_grid_power = calc_grid_power[1]
        out.state = res.state
        out.state_text = self._interpret_state(state=res.state)
        out.active_power = res.active_power
        out.charge_power = calc_charge_power[0]
        out.discharge_power = calc_charge_power[1]
        out.apparent_power = res.apparent_power
        out.error_code = res.error_code
        out.total_charged_energy = res.total_charged_energy
        out.number_modules = res.number_modules
        out.installed_capacity = res.installed_capacity
        out.serial = res.serial
        return out

    def get_raw_data_modbus(self):
        # get all known registers
        return self.modbus_client.get_all_data_modbus()

    def get_info_cgi(self):
        # get serial of device using xml ap
        if self.cgi_client is None:
            raise ValueError(CGI_ERR)

        info = self.cgi_client.get_info_cgi()
        # TODO: convert info into dataclasses
        return info

    def get_energy_cgi(self):
        # get energy values and charge load cycles from CGI
        if self.cgi_client is None:
            raise ValueError(CGI_ERR)

        energy = self.cgi_client.get_energy_cgi()
        # TODO: convert energy into dataclasses
        return energy

    def get_service_cgi(self):
        # get values from maintenance CGI
        if self.cgi_client is None:
            raise ValueError(CGI_ERR)

        service = self.cgi_client.get_service_cgi()
        # TODO: convert service into dataclasses
        return service

    def get_ems_cgi(self):
        # get ems values
        if self.cgi_client is None:
            raise ValueError(CGI_ERR)

        ems = self.cgi_client.get_ems_cgi()
        # TODO: convert ems into dataclasses
        return ems

    @staticmethod
    def _interpret_state(state: int) -> str:
        # "BUSY" (e.g. during startup) = 0/ "RUN" (ready to charge / discharge) = 1/
        # "CHARGE" = 2/ "DISCHARGE" = 3/ "STANDBY" = 4 /"ERROR" = 5 /
        # "PASSIVE" (service) = 6/ "ISLANDING" = 7
        states_map = {
            0: "BUSY",
            1: "READY",
            2: "CHARGE",
            3: "DISCHARGE",
            4: "STANDBY",
            5: "ERROR",
            6: "SERVICE",
            7: "ISLANDING",
        }
        return states_map.get(state, "")

    @staticmethod
    def _calculate_to_from_grid(grid_power: int) -> Tuple[int, int]:
        to_grid = 0
        from_grid = 0

        if grid_power >= 0:
            to_grid = abs(grid_power)
        else:
            from_grid = abs(grid_power)

        return (to_grid, from_grid)

    @staticmethod
    def _calculate_charge_discharge(active_power) -> Tuple[int, int]:
        charge_power = 0
        discharge_power = 0

        if active_power >= 0:
            charge_power = abs(active_power)
        elif active_power < 0:
            discharge_power = abs(active_power)

        return (charge_power, discharge_power)
