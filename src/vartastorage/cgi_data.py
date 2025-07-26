from dataclasses import dataclass


@dataclass
class InfoData:
    # /cgi/info.js data
    # TODO: Add IP (str), Netmask (str), Gateway (str), DNS (str) if needed.
    #       There are also gridcode (int), capacity_mode (int),
    #       P_EMS_Max (int), P_EMS_MaxDisc (int) and SW_Version_NA (list[str]) fields
    device_description: str | None
    display_serial: str | None
    sw_id_ems: int | None
    hw_id_ems: int | None
    countrycode: int | None
    sw_version_ems: str | None
    anz_charger: int | None
    soll_charger: int | None
    serial_emeter: str | None
    mac_emeter: str | None
    sw_version_emeter: str | None
    bl_version_emeter: str | None
    hw_id_emeter: int | None
    serial_wr: str | None
    mac_wr: int | None  # TODO: Check if this is correct
    sw_id_wr: int | None
    hw_id_wr: int | None
    sw_version_wr: str | None
    bl_version_wr: str | None
    serial_ens: str | None
    mac_ens: int | None  # TODO: Check if this is correct
    sw_id_ens: int | None
    hw_id_ens: int | None
    sw_version_ens: str | None
    bl_version_ens: str | None
    charger_serial: list[str]
    charger_mac: list[str]
    sw_id_charger: list[int]
    hw_id_charger: list[int]
    sw_version_charger: list[str]
    bl_version_charger: list[str]
    p_ems_max: int | None
    p_ems_maxdisc: int | None
    battery_sw: list[str]
    battery_hw: list[str]
    battery_serial: list[str]
    bm_update: list[str]
    bm_update_sw: list[str]
    bm_production: list[str]
    lg_battery_serial: list[str]

    @classmethod
    def from_dict(cls, info: dict) -> "InfoData":
        return cls(
            device_description=info.get("Device_Description"),
            display_serial=info.get("Display_Serial"),
            sw_id_ems=info.get("SW_ID_EMS"),
            hw_id_ems=info.get("HW_ID_EMS"),
            countrycode=info.get("countrycode"),
            sw_version_ems=info.get("SW_Version_EMS"),
            anz_charger=info.get("Anz_Charger"),
            soll_charger=info.get("Soll_Charger"),
            serial_emeter=info.get("Serial_EMeter"),
            mac_emeter=info.get("MAC_EMeter"),
            sw_version_emeter=info.get("SW_Version_EMeter"),
            bl_version_emeter=info.get("BL_Version_EMeter"),
            hw_id_emeter=info.get("HW_ID_EMeter"),
            serial_wr=info.get("Serial_WR"),
            mac_wr=info.get("MAC_WR"),
            sw_id_wr=info.get("SW_ID_WR"),
            hw_id_wr=info.get("HW_ID_WR"),
            sw_version_wr=info.get("SW_Version_WR"),
            bl_version_wr=info.get("BL_Version_WR"),
            serial_ens=info.get("Serial_ENS"),
            mac_ens=info.get("MAC_ENS"),
            sw_id_ens=info.get("SW_ID_ENS"),
            hw_id_ens=info.get("HW_ID_ENS"),
            sw_version_ens=info.get("SW_Version_ENS"),
            bl_version_ens=info.get("BL_Version_ENS"),
            charger_serial=info.get("Charger_Serial", []),
            charger_mac=info.get("Charger_MAC", []),
            sw_id_charger=info.get("SW_ID_Charger", []),
            hw_id_charger=info.get("HW_ID_Charger", []),
            sw_version_charger=info.get("SW_Version_Charger", []),
            bl_version_charger=info.get("BL_Version_Charger", []),
            p_ems_max=info.get("P_EMS_Max"),
            p_ems_maxdisc=info.get("P_EMS_MaxDisc"),
            battery_sw=info.get("BatterySW", []),
            battery_hw=info.get("BatteryHW", []),
            battery_serial=info.get("BatterySerial", []),
            bm_update=info.get("BM_Update", []),
            bm_update_sw=info.get("BM_UpdateSW", []),
            bm_production=info.get("BM_Production", []),
            lg_battery_serial=info.get("LG_Battery_Serial", []),
        )


@dataclass
class EnergyData:
    # /cgi/energy.js data
    total_grid_ac_dc: float  # kWh
    total_grid_dc_ac: float  # kWh
    total_inverter_ac_dc: float  # kWh
    total_inverter_dc_ac: float  # kWh
    total_charge_cycles: list[int]  # list of cycles per charger

    @classmethod
    def from_dict(cls, energy: dict) -> "EnergyData":
        return cls(
            total_grid_ac_dc=energy.get("EGrid_AC_DC", 0) / 1000,
            total_grid_dc_ac=energy.get("EGrid_DC_AC", 0) / 1000,
            total_inverter_ac_dc=energy.get("EWr_AC_DC", 0) / 1000,
            total_inverter_dc_ac=energy.get("EWr_DC_AC", 0) / 1000,
            total_charge_cycles=energy.get("Chrg_LoadCycles", []),
        )


@dataclass
class ServiceData:
    # /cgi/user_serv.js data
    hours_until_filter_maintenance: int | None  # Hours
    status_fan: int | None
    status_main: int | None

    @classmethod
    def from_dict(cls, service: dict) -> "ServiceData":
        return cls(
            hours_until_filter_maintenance=service.get("FilterZeit"),
            status_fan=service.get("Fan"),
            status_main=service.get("Main"),
        )


@dataclass
class WrData:
    nominal_power: int | None  # W
    u_verbund_l1: int | None  # V
    u_verbund_l2: int | None  # V
    u_verbund_l3: int | None  # V
    i_verbund_l1: int | None  # A
    i_verbund_l2: int | None  # A
    i_verbund_l3: int | None  # A
    u_insel_l1: int | None  # V
    u_insel_l2: int | None  # V
    u_insel_l3: int | None  # V
    i_insel_l1: int | None  # A
    i_insel_l2: int | None  # A
    i_insel_l3: int | None  # A
    temp_l1: int | None  # Celcius
    temp_l2: int | None  # Celcius
    temp_l3: int | None  # Celcius
    temp_board: int | None  # Celcius
    frequency_grid: int | None  # Hz
    online_status: int | None  # 0=Offline, 1=Online
    fan_speed: int | None  # percentage

    @classmethod
    def from_dict(cls, wr: dict) -> "WrData":
        return cls(
            nominal_power=wr.get("PSoll"),
            u_verbund_l1=wr.get("U Verbund L1"),
            u_verbund_l2=wr.get("U Verbund L2"),
            u_verbund_l3=wr.get("U Verbund L3"),
            i_verbund_l1=wr.get("I Verbund L1"),
            i_verbund_l2=wr.get("I Verbund L2"),
            i_verbund_l3=wr.get("I Verbund L3"),
            u_insel_l1=wr.get("U Insel L1"),
            u_insel_l2=wr.get("U Insel L2"),
            u_insel_l3=wr.get("U Insel L3"),
            i_insel_l1=wr.get("I Insel L1"),
            i_insel_l2=wr.get("I Insel L2"),
            i_insel_l3=wr.get("I Insel L3"),
            temp_l1=wr.get("Temp L1"),
            temp_l2=wr.get("Temp L2"),
            temp_l3=wr.get("Temp L3"),
            temp_board=wr.get("TBoard"),
            frequency_grid=wr.get("FNetz"),
            online_status=wr.get("OnlineStatus"),
            fan_speed=wr.get("Luefter"),
        )


@dataclass
class EMeterData:
    f_netz: int | None
    sens_state: int | None
    u_v_l1: int | None
    u_v_l2: int | None
    u_v_l3: int | None
    iw_v_l1: int | None
    iw_v_l2: int | None
    iw_v_l3: int | None
    ib_v_l1: int | None
    ib_v_l2: int | None
    ib_v_l3: int | None
    is_v_l1: int | None
    is_v_l2: int | None
    is_v_l3: int | None
    iw_pv_l1: int | None
    iw_pv_l2: int | None
    iw_pv_l3: int | None
    ib_pv_l1: int | None
    ib_pv_l2: int | None
    ib_pv_l3: int | None
    is_pv_l1: int | None
    is_pv_l2: int | None
    is_pv_l3: int | None

    @classmethod
    def from_dict(cls, emeter: dict) -> "EMeterData":
        return cls(
            f_netz=emeter.get("FNetz"),
            sens_state=emeter.get("SensState"),
            u_v_l1=emeter.get("U_V_L1"),
            u_v_l2=emeter.get("U_V_L2"),
            u_v_l3=emeter.get("U_V_L3"),
            iw_v_l1=emeter.get("Iw_V_L1"),
            iw_v_l2=emeter.get("Iw_V_L2"),
            iw_v_l3=emeter.get("Iw_V_L3"),
            ib_v_l1=emeter.get("Ib_V_L1"),
            ib_v_l2=emeter.get("Ib_V_L2"),
            ib_v_l3=emeter.get("Ib_V_L3"),
            is_v_l1=emeter.get("Is_V_L1"),
            is_v_l2=emeter.get("Is_V_L2"),
            is_v_l3=emeter.get("Is_V_L3"),
            iw_pv_l1=emeter.get("Iw_PV_L1"),
            iw_pv_l2=emeter.get("Iw_PV_L2"),
            iw_pv_l3=emeter.get("Iw_PV_L3"),
            ib_pv_l1=emeter.get("Ib_PV_L1"),
            ib_pv_l2=emeter.get("Ib_PV_L2"),
            ib_pv_l3=emeter.get("Ib_PV_L3"),
            is_pv_l1=emeter.get("Is_PV_L1"),
            is_pv_l2=emeter.get("Is_PV_L2"),
            is_pv_l3=emeter.get("Is_PV_L3"),
        )


@dataclass
class EnsData:
    f_netz: int | None
    u_v_l1: int | None
    u_v_l2: int | None
    u_v_l3: int | None

    @classmethod
    def from_dict(cls, ens: dict) -> "EnsData":
        return cls(
            f_netz=ens.get("FNetz"),
            u_v_l1=ens.get("U_V_L1"),
            u_v_l2=ens.get("U_V_L2"),
            u_v_l3=ens.get("U_V_L3"),
        )


@dataclass
class ChargerData:
    # TODO
    pass


@dataclass
class BattData:
    # TODO
    pass
