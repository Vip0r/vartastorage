from typing import Tuple

from vartastorage.cgi_client import CgiClient
from vartastorage.modbus_client import ModbusClient


class VartaStorage:
    def __init__(self, modbus_host, modbus_port, username=None, password=None):
        # connect to modbus server
        self.modbus_client = ModbusClient(modbus_host, modbus_port)
        # connect to cgi
        self.cgi_client = CgiClient(modbus_host, username, password)

    def get_all_data_modbus(self):
        # TODO: integrate 'all_data' with calculated data
        pass

    def get_raw_data_modbus(self):
        # get all known registers
        return self.modbus_client.get_all_data_modbus()

    def get_state_modbus(self):
        # state of system
        return self._interpret_state(self.modbus_client.get_state_modbus())

    def get_charge_power_modbus(self):
        # active power in Watt; measured at internal inverter;
        # positive:charge; negative:discharge;
        return self._calculate_charge_discharge(
            self.modbus_client.get_active_power_modbus()
        )

    def get_grid_power_modbus(self):
        # grid power in Watt; measured at household grid connection point
        return self._calculate_to_from_grid(self.modbus_client.get_grid_power_modbus())

    def get_info_cgi(self):
        # get serial of device using xml ap
        info = self.cgi_client.get_info_cgi()
        # TODO: convert info into dataclasses
        return info

    def get_energy_cgi(self):
        # get energy values and charge load cycles from CGI
        energy = self.cgi_client.get_energy_cgi()
        # TODO: convert energy into dataclasses
        return energy

    def get_service_cgi(self):
        # get values from maintenance CGI
        service = self.cgi_client.get_service_cgi()
        # TODO: convert service into dataclasses
        return service

    def get_ems_cgi(self):
        # get ems values
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