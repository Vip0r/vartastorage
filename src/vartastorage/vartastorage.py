from dataclasses import dataclass
from typing import Tuple

from vartastorage.cgi_client import CgiClient
from vartastorage.modbus_client import ModbusClient

CGI_ERR = "The CgiClient is not initialized. Did you set cgi=False?"


@dataclass
class VartaStorageData:
    # raw modbus data
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

    # modbus interpretations
    state_text: str = ""
    to_grid_power: int = 0
    from_grid_power: int = 0
    charge_power: int = 0
    discharge_power: int = 0

    # /cgi/info.js data
    device_description: str = ""
    display_serial: str = ""
    sw_id_ems: int = 0
    hw_id_ems: int = 0
    countrycode: int = 0
    sw_version_ems: str = ""
    anz_charger: int = 0
    soll_charger: int = 0
    serial_emeter: str = ""
    mac_emeter: str = ""
    sw_version_emeter: str = ""
    bl_version_emeter: str = ""
    hw_id_emeter: int = 0
    serial_wr: str = ""
    mac_wr: int = 0
    sw_id_wr: int = 0
    hw_id_wr: int = 0
    sw_version_wr: str = ""
    bl_version_wr: str = ""
    serial_ens: str = ""
    mac_ens: int = 0
    sw_id_ens: int = 0
    mac_ens: int = 0
    hw_id_ens: int = 0
    sw_version_ens: str = ""
    bl_version_ens: str = ""
    charger_serial: str = ""
    charger_mac: str = ""
    sw_id_charger: str = ""
    hw_id_charger: str = ""
    sw_version_charger: str = ""
    bl_version_charger: str = ""
    p_ems_max: int = ""
    p_ems_maxdisc: int = 0
    batterysw: str = ""
    batteryhw: str = ""
    batteryserial: str = ""
    bm_update: str = ""
    bm_updatesw: str = ""
    bm_production: str = ""
    lg_battery_serial: str = ""

    # /cgi/energy.js data
    total_grid_ac_dc: int = 0  # Wh
    total_grid_dc_ac: int = 0  # Wh
    total_inverter_ac_dc: int = 0  # Wh
    total_inverter_dc_ac: int = 0  # Wh
    total_charge_cycles: int = 0

    # /cgi/user_serv.js data
    hours_until_filter_maintenance: int = 0  # Hours
    status_fan: int = 0
    status_main: int = 0

    # /cgi/ems_datajs data
    nominal_power: int = 0  # W
    u_verbund_l1: int = 0  # V
    u_verbund_l2: int = 0  # V
    u_verbund_l3: int = 0  # V
    i_verbund_l1: int = 0  # A
    i_verbund_l2: int = 0  # A
    i_verbund_l3: int = 0  # A
    u_insel_l1: int = 0  # V
    u_insel_l2: int = 0  # V
    u_insel_l3: int = 0  # V
    i_insel_l1: int = 0  # A
    i_insel_l2: int = 0  # A
    i_insel_l3: int = 0  # A
    temp_l1: int = 0  # Celcius
    temp_l2: int = 0  # Celcius
    temp_l3: int = 0  # Celcius
    temp_board: int = 0  # Celcius
    frequency_grid: int = 0  # Hz
    online_status: int = 0  # 0=Offline, 1=Online
    fan_speed: int = 0  # percentage


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
        # retrieve available data points in /cgi/info.js
        if self.cgi_client is None:
            raise ValueError(CGI_ERR)

        out = VartaStorageData
        info = self.cgi_client.get_info_cgi()
        if "Device_Description" in info:
            out.device_description = info["Device_Description"]  #
        if "Display_Serial" in info:
            out.display_serial = info["Display_Serial"]
        if "SW_ID_EMS" in info:
            out.sw_id_ems = info["SW_ID_EMS"]
        if "HW_ID_EMS" in info:
            out.hw_id_ems = info["HW_ID_EMS"]
        if "countrycode" in info:
            out.countrycode = info["countrycode"]
        if "SW_Version_EMS" in info:
            out.sw_version_ems = info["SW_Version_EMS"]
        if "Anz_Charger" in info:
            out.anz_charger = info["Anz_Charger"]
        if "Soll_Charger" in info:
            out.soll_charger = info["Soll_Charger"]
        if "Serial_EMeter" in info:
            out.serial_emeter = info["Serial_EMeter"]
        if "MAC_EMeter" in info:
            out.mac_emeter = info["MAC_EMeter"]
        if "SW_Version_EMeter" in info:
            out.sw_version_emeter = info["SW_Version_EMeter"]
        if "BL_Version_EMeter" in info:
            out.bl_version_emeter = info["BL_Version_EMeter"]
        if "HW_ID_EMeter" in info:
            out.hw_id_emeter = info["HW_ID_EMeter"]
        if "Serial_WR" in info:
            out.serial_wr = info["Serial_WR"]
        if "MAC_WR" in info:
            out.mac_wr = info["MAC_WR"]
        if "SW_ID_WR" in info:
            out.sw_id_wr = info["SW_ID_WR"]
        if "HW_ID_WR" in info:
            out.hw_id_wr = info["HW_ID_WR"]
        if "SW_Version_WR" in info:
            out.sw_version_wr = info["SW_Version_WR"]
        if "BL_Version_WR" in info:
            out.bl_version_wr = info["BL_Version_WR"]
        if "Serial_ENS" in info:
            out.serial_ens = info["Serial_ENS"]
        if "MAC_ENS" in info:
            out.mac_ens = info["MAC_ENS"]
        if "SW_ID_ENS" in info:
            out.sw_id_ens = info["SW_ID_ENS"]
        if "HW_ID_ENS" in info:
            out.hw_id_ens = info["HW_ID_ENS"]
        if "SW_Version_ENS" in info:
            out.sw_version_ens = info["SW_Version_ENS"]
        if "BL_Version_ENS" in info:
            out.bl_version_ens = info["BL_Version_ENS"]
        if "Charger_Serial" in info:
            out.charger_serial = info["Charger_Serial"]
        if "Charger_MAC" in info:
            out.charger_mac = info["Charger_MAC"]
        if "SW_ID_Charger" in info:
            out.sw_id_charger = info["SW_ID_Charger"]
        if "HW_ID_Charger" in info:
            out.hw_id_charger = info["HW_ID_Charger"]
        if "SW_Version_Charger" in info:
            out.sw_version_charger = info["SW_Version_Charger"]
        if "BL_Version_Charger" in info:
            out.bl_version_charger = info["BL_Version_Charger"]
        if "P_EMS_Max" in info:
            out.p_ems_max = info["P_EMS_Max"]
        if "P_EMS_MaxDisc" in info:
            out.p_ems_maxdisc = info["P_EMS_MaxDisc"]
        if "BatterySW" in info:
            out.batterysw = info["BatterySW"]
        if "BatteryHW" in info:
            out.batteryhw = info["BatteryHW"]
        if "BatterySerial" in info:
            out.batteryserial = info["BatterySerial"]
        if "BM_Update" in info:
            out.bm_update = info["BM_Update"]
        if "BM_UpdateSW" in info:
            out.bm_updatesw = info["BM_UpdateSW"]
        if "BM_Production" in info:
            out.bm_production = info["BM_Production"]
        if "LG_Battery_Serial" in info:
            out.lg_battery_serial = info["LG_Battery_Serial"]

        return out

    def get_energy_cgi(self):
        # retrieve available data points in /cgi/energy.js
        if self.cgi_client is None:
            raise ValueError(CGI_ERR)

        out = VartaStorageData
        energy = self.cgi_client.get_energy_cgi()

        if "EGrid_AC_DC" in energy:
            out.total_grid_ac_dc = energy["EGrid_AC_DC"]
        if "EGrid_DC_AC" in energy:
            out.total_grid_dc_ac = energy["EGrid_DC_AC"]
        if "EWr_AC_DC" in energy:
            out.total_inverter_ac_dc = energy["EWr_AC_DC"]
        if "EWr_DC_AC" in energy:
            out.total_inverter_dc_ac = energy["EWr_DC_AC"]
        if "Chrg_LoadCycles" in energy:
            out.total_charge_cycles = energy["Chrg_LoadCycles"][0]

        return out

    def get_service_cgi(self):
        # get values from maintenance CGI
        if self.cgi_client is None:
            raise ValueError(CGI_ERR)

        out = VartaStorageData
        service = self.cgi_client.get_service_cgi()
        if "FilterZeit" in service:
            out.hours_until_filter_maintenance = service["FilterZeit"]
        if "Fan" in service:
            out.status_fan = service["Fan"]
        if "Main" in service:
            out.status_main = service["Main"]

        return out

    def get_ems_cgi(self):
        # get ems values
        if self.cgi_client is None:
            raise ValueError(CGI_ERR)

        out = VartaStorageData
        ems = self.cgi_client.get_ems_cgi()

        if "PSoll" in ems["wr"]:
            out.nominal_power = ems["wr"]["PSoll"]
        if "U Verbund L1" in ems["wr"]:
            out.u_verbund_l1 = ems["wr"]["U Verbund L1"]
        if "U Verbund L2" in ems["wr"]:
            out.u_verbund_l2 = ems["wr"]["U Verbund L2"]
        if "U Verbund L3" in ems["wr"]:
            out.u_verbund_l3 = ems["wr"]["U Verbund L3"]
        if "I Verbund L1" in ems["wr"]:
            out.i_verbund_l1 = ems["wr"]["I Verbund L1"]
        if "I Verbund L2" in ems["wr"]:
            out.i_verbund_l2 = ems["wr"]["I Verbund L2"]
        if "I Verbund L3" in ems["wr"]:
            out.i_verbund_l3 = ems["wr"]["I Verbund L3"]
        if "U Insel L1" in ems["wr"]:
            out.u_insel_l1 = ems["wr"]["U Insel L1"]
        if "U Insel L2" in ems["wr"]:
            out.u_insel_l2 = ems["wr"]["U Insel L2"]
        if "U Insel L3" in ems["wr"]:
            out.u_insel_l3 = ems["wr"]["U Insel L3"]
        if "I Insel L1" in ems["wr"]:
            out.i_insel_l1 = ems["wr"]["I Insel L1"]
        if "I Insel L2" in ems["wr"]:
            out.i_insel_l2 = ems["wr"]["I Insel L3"]
        if "I Insel L3" in ems["wr"]:
            out.i_insel_l3 = ems["wr"]["I Insel L3"]
        if "Temp L1" in ems["wr"]:
            out.temp_l1 = ems["wr"]["Temp L1"]
        if "Temp L2" in ems["wr"]:
            out.temp_l2 = ems["wr"]["Temp L2"]
        if "Temp L3" in ems["wr"]:
            out.temp_l3 = ems["wr"]["Temp L3"]
        if "TBoard" in ems["wr"]:
            out.temp_board = ems["wr"]["TBoard"]
        if "FNetz" in ems["wr"]:
            out.frequency_grid = ems["wr"]["FNetz"]
        if "OnlineStatus" in ems["wr"]:
            out.online_status = ems["wr"]["OnlineStatus"]
        if "Luefter" in ems["wr"]:
            out.fan_speed = ems["wr"]["Luefter"]

        return out

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
