# coding: utf-8

from datetime import datetime

from .client import Client


class VartaStorage(object):
    def __init__(self, modbus_host, modbus_port, password):
        # connect to modbus server
        self.client = Client(modbus_host, modbus_port, password)

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
        self.error_code = data["error_code"]
        self.total_charged_energy = data["total_charged_energy"]
        self.serial = data["serial"]
        self.get_energy_cgi()
        self.get_service_cgi()
        # self.get_ems_cgi()

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

    def get_energy_cgi(self):
        # get energy values and charge load cycles from CGI
        # EGrid_AC_DC == Grid -> Building (Wh)
        # EGrid_DC_AC == Home -> Grid (Wh)
        # EWr_AC_DC == Inverter AC -> DC == Total Charged (Wh)
        # EWr_DC_AC == Inverter DC -> AC == Total Discharged (Wh)
        # Chrg_LoadCycles == Charge Cycle Counter
        energycgidata = self.client.get_energy_cgi()
        self.grid_to_home = energycgidata["EGrid_AC_DC"]
        self.home_to_grid = energycgidata["EGrid_DC_AC"]
        self.inverter_total_charged = energycgidata["EWr_AC_DC"]
        self.inverter_total_discharged = energycgidata["EWr_DC_AC"]
        self.charge_cycle_counter = energycgidata["Chrg_LoadCycles"]

    def get_service_cgi(self):
        # get values from maintenance CGI
        # hours_until_filter_maintenance
        # fan state
        # main is now yet known / undocumented
        servicecgidata = self.client.get_service_cgi()
        self.hours_until_filter_maintenance = servicecgidata["FilterZeit"]
        self.fan = servicecgidata["Fan"]
        self.main = servicecgidata["Main"]

    def get_ems_cgi(self):
        # get ems values
        emscgidata = self.client.get_ems_cgi()
        self.FNetz = emscgidata["FNetz"]
        self.U_V_L1 = emscgidata["U_V_L1"]
        self.U_V_L2 = emscgidata["U_V_L2"]
        self.U_V_L3 = emscgidata["U_V_L3"]
        self.Iw_V_L1 = emscgidata["Iw_V_L1"]
        self.Iw_V_L2 = emscgidata["Iw_V_L2"]
        self.Iw_V_L3 = emscgidata["Iw_V_L3"]
        self.Ib_V_L1 = emscgidata["Ib_V_L1"]
        self.Ib_V_L2 = emscgidata["Ib_V_L2"]
        self.Ib_V_L3 = emscgidata["Ib_V_L3"]
        self.Is_V_L1 = emscgidata["Is_V_L1"]
        self.Is_V_L2 = emscgidata["Is_V_L2"]
        self.Is_V_L3 = emscgidata["Is_V_L3"]
        self.Iw_PV_L1 = emscgidata["Iw_PV_L1"]
        self.Iw_PV_L2 = emscgidata["Iw_PV_L2"]
        self.Iw_PV_L3 = emscgidata["Iw_PV_L3"]
        self.Ib_PV_L1 = emscgidata["Ib_PV_L1"]
        self.Ib_PV_L2 = emscgidata["Ib_PV_L2"]
        self.Ib_PV_L3 = emscgidata["Ib_PV_L3"]
        self.Is_PV_L1 = emscgidata["Is_PV_L1"]
        self.Is_PV_L2 = emscgidata["Is_PV_L2"]
        self.Is_PV_L3 = emscgidata["Is_PV_L3"]

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
