# coding: utf-8

from datetime import datetime

from vartastorage.modbus_client import Client


class VartaStorage(object):
    def __init__(self, modbus_host, modbus_port):
        # connect to modbus server
        self.client = Client(modbus_host, modbus_port)

    def get_all_data(self):
        # get all known registers

        data = self.client.get_all_data()
        self.grid_power = data["grid_power"]
        self.soc = data["soc"]
        self.state = data["state"]
        self.active_power = data["active_power"]
        self.apparent_power = data["apparent_power"]
        self.production_power = data["production_power"]
        self.total_production_power = data["total_production_power"]
        self.error_code = data["error_code"]

    def get_grid_power(self):
        # grid power in Watt; measured at household grid connection point
        # register 1078, size 1, SINT16

        self.grid_power = self.client.get_soc()

    def get_soc(self):
        # total state of charge in %
        # register 1068, size 1, UINT16

        self.soc = self.client.get_soc()

    def get_state(self):
        # state of system
        # "BUSY" (e.g. during startup) = 0/ "RUN" (ready to charge / discharge) = 1/
        # "CHARGE" = 2/ "DISCHARGE" = 3/ "STANDBY" = 4 /"ERROR" = 5 / "PASSIVE" (service) = 6/ "ISLANDING" = 7
        # register 1065, size 1, UINT16

        self.state = self.client.get_state()

    def get_active_power(self):
        # active power in Watt; measured at internal inverter; positive:charge; negative:discharge
        # register 1066, size 1, SINT16

        self.active_power = self.client.get_active_power()

    def get_apparent_power(self):
        # apparent power in VA; measured at internal inverter; positive:charge; negative:discharge
        # register 1067, size 1, SINT16

        self.apparent_power = self.client.get_apparent_power()

    def get_production_power(self):
        # current production_power power in W
        # register 1100, size 1, UINT16

        self.apparent_power = self.client.get_production_power()

    def get_total_production_power(self):
        # total production_power power for whole day in kWh 
        # register 1101, size 1, U16FX2

        self.apparent_power = self.client.get_total_production_power()

    def get_error_code(self):
        # errorcode EMS
        # register 1072, size 1, UINT16

        self.apparent_power = self.client.get_error_code()