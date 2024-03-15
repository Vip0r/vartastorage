# coding: utf-8

from datetime import datetime

from vartastorage.client import Client


class VartaStorage(object):
    def __init__(self, modbus_host, modbus_port):
        # connect to modbus server
        self.client = Client(modbus_host, modbus_port)

    def get_all_data(self):
        # get all known registers
        data = self.client.get_all_data()
        self.grid_power = data["grid_power"]
        self.calculate_to_from_grid()  # create dedicated properties (grid consumption and grid supply)
        self.soc = data["soc"]
        self.state = data["state"]
        self.interpret_state()  # interpret state value into a human readbale string
        self.active_power = data["active_power"]
        self.calculate_charge_discharge()  # create dedicated properties for charge and discharge
        self.apparent_power = data["apparent_power"]
        self.production_power = data["production_power"]
        self.total_production_power = data["total_production_power"]
        self.error_code = data["error_code"]
        self.total_charged_energy = data["total_charged_energy"]
        self.serial = data["serial"]

    def get_grid_power(self):
        # grid power in Watt; measured at household grid connection point
        # register 1078, size 1, SINT16

        self.grid_power = self.client.get_grid_power()
        self.calculate_to_from_grid()

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
        self.interpret_state()

    def get_active_power(self):
        # active power in Watt; measured at internal inverter; positive:charge; negative:discharge
        # register 1066, size 1, SINT16

        self.active_power = self.client.get_active_power()
        self.calculate_charge_discharge()

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

    def get_total_charged_energy(self):
        # total charged energy in kWh
        # register 1069(low byte) and 1070 (high byte), size 1, UINT16

        self.apparent_power = self.client.get_total_charged_energy()

    def get_serial(self):
        # get serial of device using xml api (modbus registers are not documented properly)

        self.serial = self.client.get_serial()

    def interpret_state(self):
        # "BUSY" (e.g. during startup) = 0/ "RUN" (ready to charge / discharge) = 1/
        # "CHARGE" = 2/ "DISCHARGE" = 3/ "STANDBY" = 4 /"ERROR" = 5 / "PASSIVE" (service) = 6/ "ISLANDING" = 7
        if type(self.state) == int:
            if self.state == 0:
                self.state_text = "BUSY"
            elif self.state == 1:
                self.state_text = "READY"
            elif self.state == 2:
                self.state_text = "CHARGE"
            elif self.state == 3:
                self.state_text = "DISCHARGE"
            elif self.state == 4:
                self.state_text = "STANDBY"
            elif self.state == 5:
                self.state_text = "ERROR"
            elif self.state == 6:
                self.state_text = "SERVICE"
            elif self.state == 7:
                self.state_text = "ISLANDING"
            else:
                self.state_text = ""
        else:
            self.state_text = None

    def calculate_to_from_grid(self):
        if type(self.grid_power) == int:
            if self.grid_power >= 0:
                self.to_grid_power = abs(self.grid_power)
                self.from_grid_power = 0
            elif self.grid_power < 0:
                self.from_grid_power = abs(self.grid_power)
                self.to_grid_power = 0
        else:
            self.to_grid_power = None
            self.from_grid_power = None

    def calculate_charge_discharge(self):
        if type(self.active_power) == int:
            if self.active_power >= 0:
                self.charge_power = abs(self.active_power)
                self.discharge_power = 0
            elif self.active_power < 0:
                self.discharge_power = abs(self.active_power)
                self.charge_power = 0
        else:
            self.charge_power = None
            self.discharge_power = None
