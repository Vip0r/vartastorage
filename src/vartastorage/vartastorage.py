from dataclasses import dataclass

from vartastorage.cgi_client import CgiClient
from vartastorage.cgi_data import EmsData, EnergyData, InfoData, ServiceData, WrData
from vartastorage.modbus_client import ModbusClient, ModbusData

CGI_ERR = "The CgiClient is not initialized. Did you set cgi=False?"


@dataclass
class BaseData(ModbusData):
    # modbus interpretations
    state_text: str = ""
    to_grid_power: int = 0
    from_grid_power: int = 0
    charge_power: int = 0
    discharge_power: int = 0


@dataclass
class VartaStorageData:
    modbus_data: ModbusData
    info_data: InfoData | None = None
    service_data: ServiceData | None = None
    ems_data: EmsData | None = None
    energy_data: EnergyData | None = None


class VartaStorage:
    def __init__(
        self, modbus_host, modbus_port, cgi=True, username=None, password=None
    ):
        # connect to modbus server
        self.modbus_client = ModbusClient(modbus_host, modbus_port)

        # connect to cgi
        if cgi:
            self.cgi_client = CgiClient(modbus_host, username, password)

    def get_all_data(self) -> VartaStorageData:
        out = VartaStorageData(modbus_data=self.get_all_data_modbus())

        if self.cgi_client is not None:
            out.ems_data = self.get_ems_cgi()
            out.energy_data = self.get_energy_cgi()
            out.info_data = self.get_info_cgi()
            out.service_data = self.get_service_cgi()

        return out

    def get_all_data_modbus(self) -> BaseData:
        res = self.get_raw_data_modbus()

        calc_grid_power = self._calculate_to_from_grid(res.grid_power)
        calc_charge_power = self._calculate_charge_discharge(res.active_power)

        return BaseData(
            soc=res.soc,
            grid_power=res.grid_power,
            state=res.state,
            active_power=res.active_power,
            apparent_power=res.apparent_power,
            error_code=res.error_code,
            total_charged_energy=res.total_charged_energy,
            number_modules=res.number_modules,
            installed_capacity=res.installed_capacity,
            serial=res.serial,
            state_text=self._interpret_state(state=res.state),
            to_grid_power=calc_grid_power[0],
            from_grid_power=calc_grid_power[1],
            charge_power=calc_charge_power[0],
            discharge_power=calc_charge_power[1],
        )

    def get_raw_data_modbus(self) -> ModbusData:
        # get all known registers
        return self.modbus_client.get_all_data_modbus()

    def get_info_cgi(self) -> InfoData:
        # retrieve available data points in /cgi/info.js
        if self.cgi_client is None:
            raise ValueError(CGI_ERR)

        info = self.cgi_client.get_info_cgi()
        return InfoData(
            device_description=info.get("Device_Description", None),
            display_serial=info.get("Display_Serial", None),
            sw_id_ems=info.get("SW_ID_EMS", None),
            hw_id_ems=info.get("HW_ID_EMS", None),
            countrycode=info.get("countrycode", None),
            sw_version_ems=info.get("SW_Version_EMS", None),
            anz_charger=info.get("Anz_Charger", None),
            soll_charger=info.get("Soll_Charger", None),
            serial_emeter=info.get("Serial_EMeter", None),
            mac_emeter=info.get("MAC_EMeter", None),
            sw_version_emeter=info.get("SW_Version_EMeter", None),
            bl_version_emeter=info.get("BL_Version_EMeter", None),
            hw_id_emeter=info.get("HW_ID_EMeter", None),
            serial_wr=info.get("Serial_WR", None),
            mac_wr=info.get("MAC_WR", None),
            sw_id_wr=info.get("SW_ID_WR", None),
            hw_id_wr=info.get("HW_ID_WR", None),
            sw_version_wr=info.get("SW_Version_WR", None),
            bl_version_wr=info.get("BL_Version_WR", None),
            serial_ens=info.get("Serial_ENS", None),
            mac_ens=info.get("MAC_ENS", None),
            sw_id_ens=info.get("SW_ID_ENS", None),
            hw_id_ens=info.get("HW_ID_ENS", None),
            sw_version_ens=info.get("SW_Version_ENS", None),
            bl_version_ens=info.get("BL_Version_ENS", None),
            charger_serial=info.get("Charger_Serial", None),
            charger_mac=info.get("Charger_MAC", None),
            sw_id_charger=info.get("SW_ID_Charger", None),
            hw_id_charger=info.get("HW_ID_Charger", None),
            sw_version_charger=info.get("SW_Version_Charger", None),
            bl_version_charger=info.get("BL_Version_Charger", None),
            p_ems_max=info.get("P_EMS_Max", None),
            p_ems_maxdisc=info.get("P_EMS_MaxDisc", None),
            battery_sw=info.get("BatterySW", None),
            battery_hw=info.get("BatteryHW", None),
            battery_serial=info.get("BatterySerial", None),
            bm_update=info.get("BM_Update", None),
            bm_update_sw=info.get("BM_UpdateSW", None),
            bm_production=info.get("BM_Production", None),
            lg_battery_serial=info.get("LG_Battery_Serial", None),
        )

    def get_energy_cgi(self) -> EnergyData:
        # retrieve available data points in /cgi/energy.js
        if self.cgi_client is None:
            raise ValueError(CGI_ERR)

        energy = self.cgi_client.get_energy_cgi()
        return EnergyData(
            total_grid_ac_dc=energy.get("EGrid_AC_DC", None),
            total_grid_dc_ac=energy.get("EGrid_DC_AC", None),
            total_inverter_ac_dc=energy.get("EWr_AC_DC", None),
            total_inverter_dc_ac=energy.get("EWr_DC_AC", None),
            total_charge_cycles=energy.get("Chrg_LoadCycles", None),
        )

    def get_service_cgi(self) -> ServiceData:
        # get values from maintenance CGI
        if self.cgi_client is None:
            raise ValueError(CGI_ERR)

        service = self.cgi_client.get_service_cgi()
        return ServiceData(
            hours_until_filter_maintenance=service.get("FilterZeit", None),
            status_fan=service.get("Fan", None),
            status_main=service.get("Main", None),
        )

    def get_ems_cgi(self) -> EmsData:
        # get ems values
        if self.cgi_client is None:
            raise ValueError(CGI_ERR)

        ems = self.cgi_client.get_ems_cgi()

        out = EmsData()
        if "wr" in ems:
            wr = ems["wr"]
            out.wr_data = WrData(
                nominal_power=wr.get("PSoll", None),
                u_verbund_l1=wr.get("U Verbund L1", None),
                u_verbund_l2=wr.get("U Verbund L2", None),
                u_verbund_l3=wr.get("U Verbund L3", None),
                i_verbund_l1=wr.get("I Verbund L1", None),
                i_verbund_l2=wr.get("I Verbund L2", None),
                i_verbund_l3=wr.get("I Verbund L3", None),
                u_insel_l1=wr.get("U Insel L1", None),
                u_insel_l2=wr.get("U Insel L2", None),
                u_insel_l3=wr.get("U Insel L3", None),
                i_insel_l1=wr.get("I Insel L1", None),
                i_insel_l2=wr.get("I Insel L2", None),
                i_insel_l3=wr.get("I Insel L3", None),
                temp_l1=wr.get("Temp L1", None),
                temp_l2=wr.get("Temp L2", None),
                temp_l3=wr.get("Temp L3", None),
                temp_board=wr.get("TBoard", None),
                frequency_grid=wr.get("FNetz", None),
                online_status=wr.get("OnlineStatus", None),
                fan_speed=wr.get("Luefter", None),
            )
        # TODO: add more if necessary

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
    def _calculate_to_from_grid(grid_power: int) -> tuple[int, int]:
        to_grid = 0
        from_grid = 0

        if grid_power >= 0:
            to_grid = abs(grid_power)
        else:
            from_grid = abs(grid_power)

        return (to_grid, from_grid)

    @staticmethod
    def _calculate_charge_discharge(active_power) -> tuple[int, int]:
        charge_power = 0
        discharge_power = 0

        if active_power >= 0:
            charge_power = abs(active_power)
        elif active_power < 0:
            discharge_power = abs(active_power)

        return (charge_power, discharge_power)
