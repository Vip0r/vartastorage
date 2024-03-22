from vartastorage.cgi_client import CgiClient
from vartastorage.modbus_client import ModbusClient


class VartaStorage:
    def __init__(self, modbus_host, modbus_port, username=None, password=None):
        # connect to modbus server
        self.modbus_client = ModbusClient(modbus_host, modbus_port)
        # connect to cgi
        self.cgi_client = CgiClient(modbus_host, username, password)

    def get_all_data_modbus(self):
        # get all known registers
        data = self.modbus_client.get_all_data_modbus()
        self.grid_power = data["grid_power"]
        # create dedicated properties (grid consumption and grid supply)
        self.calculate_to_from_grid()
        self.soc = data["soc"]
        self.state = data["state"]
        # interpret state value into a human readbale string
        self.interpret_state()
        self.active_power = data["active_power"]
        # create dedicated properties for charge and discharge
        self.calculate_charge_discharge()
        self.apparent_power = data["apparent_power"]
        self.error_code = data["error_code"]
        self.total_charged_energy = data["total_charged_energy"]
        self.serial = data["serial"]
        self.number_modules = data["number_modules"]
        self.installed_capacity = data["installed_capacity"]

    def get_all_data_cgi(self):
        # get all known registers
        self.get_energy_cgi()
        self.get_service_cgi()
        self.get_ems_cgi()

    def get_serial_modbus(self):
        # get serial of device using modbus
        # Supported on VARTA element, pulse, pulse neo, link and flex storage devices
        # register 1054, size 1, STRING10, 9Digits

        self.serial = self.modbus_client.get_serial_modbus()

    def get_bm_modbus(self):
        # Retrieves the number of battery modules installed
        # Supported on VARTA element, pulse, pulse neo, link and flex storage devices
        # register 1064, size 1, UINT16

        self.batterymodules = self.modbus_client.get_bm_modbus

    def get_state_modbus(self):
        # state of system
        # "BUSY" (e.g. during startup) = 0/ "RUN" (ready to charge / discharge) = 1/
        # "CHARGE" = 2/ "DISCHARGE" = 3/ "STANDBY" = 4 /"ERROR" = 5 /
        # "PASSIVE" (service) = 6/ "ISLANDING" = 7
        # register 1065, size 1, UINT16

        self.state = self.modbus_client.get_state_modbus()
        self.interpret_state()

    def get_active_power_modbus(self):
        # active power in Watt; measured at internal inverter; positive:charge;
        # negative:discharge
        # Supported on VARTA element, pulse, pulse neo, link and flex storage devices
        # register 1066, size 1, SINT16

        self.active_power = self.modbus_client.get_active_power_modbus()
        self.calculate_charge_discharge()

    def get_apparent_power_modbus(self):
        # apparent power in VA; measured at internal inverter; positive:charge;
        # negative:discharge
        # Supported on VARTA element, pulse, pulse neo, link and flex storage devices
        # register 1067, size 1, SINT16

        self.apparent_power = self.modbus_client.get_apparent_power_modbus()

    def get_soc_modbus(self):
        # total state of charge in %
        # Supported on VARTA element, pulse, pulse neo, link and flex storage devices
        # register 1068, size 1, UINT16

        self.soc = self.modbus_client.get_soc_modbus()

    def get_total_charged_energy_modbus(self):
        # total charged energy in kWh
        # Supported on VARTA element, pulse, pulse neo, link and flex storage devices
        # register 1069(low byte) and 1070 (high byte), size 1, UINT16

        self.total_charged_energy = self.modbus_client.get_total_charged_energy_modbus()

    def get_installed_capacity_modbus(self):
        # installed capacity in Wh
        # Supported on VARTA element, pulse, pulse neo, link and flex storage devices
        # register 1071, size 1, UINT16

        self.installed_capacity = self.modbus_client.get_installed_capacity_modbus()

    def get_error_code_modbus(self):
        # errorcode EMS
        # Supported on VARTA element, pulse, pulse neo, link and flex storage devices
        # register 1072, size 1, UINT16

        self.apparent_power = self.modbus_client.get_error_code_modbus()

    def get_grid_power_modbus(self):
        # grid power in Watt; measured at household grid connection point
        # Supported on VARTA element, pulse, pulse neo, link and flex storage devices
        # register 1078, size 1, SINT16

        self.grid_power = self.modbus_client.get_grid_power_modbus()
        self.calculate_to_from_grid()

    def get_info_cgi(self):
        # get serial of device using xml api
        # (modbus registers are not documented properly)
        # Supported on VARTA element, pulse, pulse neo, link and flex storage devices

        self.serial = self.cgi_client.get_info_cgi()

    def get_energy_cgi(self):
        # get energy values and charge load cycles from CGI
        # EGrid_AC_DC == Grid -> Building (Wh)
        # EGrid_DC_AC == Home -> Grid (Wh)
        # EWr_AC_DC == Inverter AC -> DC == Total Charged (Wh)
        # EWr_DC_AC == Inverter DC -> AC == Total Discharged (Wh)
        # Chrg_LoadCycles == Charge Cycle Counter
        energycgidata = self.cgi_client.get_energy_cgi()
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
        servicecgidata = self.cgi_client.get_service_cgi()
        self.hours_until_filter_maintenance = servicecgidata["FilterZeit"]
        self.fan = servicecgidata["Fan"]
        self.main = servicecgidata["Main"]

    def get_ems_cgi(self):
        # get ems values
        emscgidata = self.cgi_client.get_ems_cgi()
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
        # "CHARGE" = 2/ "DISCHARGE" = 3/ "STANDBY" = 4 /"ERROR" = 5 /
        # "PASSIVE" (service) = 6/ "ISLANDING" = 7
        if isinstance(self.state, int):
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
        if isinstance(self.grid_power, int):
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
        if isinstance(self.active_power, int):
            if self.active_power >= 0:
                self.charge_power = abs(self.active_power)
                self.discharge_power = 0
            elif self.active_power < 0:
                self.discharge_power = abs(self.active_power)
                self.charge_power = 0
        else:
            self.charge_power = None
            self.discharge_power = None
