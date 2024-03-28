from dataclasses import dataclass
from typing import Tuple

from vartastorage.cgi_client import CgiClient
from vartastorage.cgi_data import (
    BattData,
    ChargerData,
    EMeterData,
    EnergyData,
    EnsData,
    InfoData,
    ServiceData,
    WrData,
)
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
class EmsData:
    # /cgi/ems_datajs data
    wr_data: WrData | None = None
    emeter_data: EMeterData | None = None
    ens_data: EnsData | None = None
    charger_data: ChargerData | None = None
    batt_data: BattData | None = None


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
        return InfoData.from_dict(info)

    def get_energy_cgi(self) -> EnergyData:
        # retrieve available data points in /cgi/energy.js
        if self.cgi_client is None:
            raise ValueError(CGI_ERR)

        energy = self.cgi_client.get_energy_cgi()
        return EnergyData.from_dict(energy)

    def get_service_cgi(self) -> ServiceData:
        # get values from maintenance CGI
        if self.cgi_client is None:
            raise ValueError(CGI_ERR)

        service = self.cgi_client.get_service_cgi()
        return ServiceData.from_dict(service)

    def get_ems_cgi(self) -> EmsData:
        # get ems values
        if self.cgi_client is None:
            raise ValueError(CGI_ERR)

        ems = self.cgi_client.get_ems_cgi()

        out = EmsData()
        if "wr" in ems:
            out.wr_data = WrData.from_dict(ems["wr"])

        if "emeter" in ems:
            out.emeter_data = EMeterData.from_dict(ems["emeter"])

        if "ens" in ems:
            out.ens_data = EnsData.from_dict(ems["ens"])

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
