from dataclasses import dataclass, field


@dataclass
class InfoData:
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
    hw_id_ens: int = 0
    sw_version_ens: str = ""
    bl_version_ens: str = ""
    charger_serial: list[str] = field(default_factory=list)
    charger_mac: list[str] = field(default_factory=list)
    sw_id_charger: list[int] = field(default_factory=list)
    hw_id_charger: list[int] = field(default_factory=list)
    sw_version_charger: list[str] = field(default_factory=list)
    bl_version_charger: list[str] = field(default_factory=list)
    p_ems_max: int = 0
    p_ems_maxdisc: int = 0
    battery_sw: list[str] = field(default_factory=list)
    battery_hw: list[str] = field(default_factory=list)
    battery_serial: list[str] = field(default_factory=list)
    bm_update: list[str] = field(default_factory=list)
    bm_update_sw: list[str] = field(default_factory=list)
    bm_production: list[str] = field(default_factory=list)
    lg_battery_serial: list[str] = field(default_factory=list)


@dataclass
class EnergyData:
    # /cgi/energy.js data
    total_grid_ac_dc: int = 0  # Wh
    total_grid_dc_ac: int = 0  # Wh
    total_inverter_ac_dc: int = 0  # Wh
    total_inverter_dc_ac: int = 0  # Wh
    total_charge_cycles: list[int] = field(default_factory=list)


@dataclass
class ServiceData:
    # /cgi/user_serv.js data
    hours_until_filter_maintenance: int = 0  # Hours
    status_fan: int = 0
    status_main: int = 0


@dataclass
class WrData:
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


@dataclass
class EMeterData:
    f_netz: int = 0
    sens_state: int = 0
    u_v_l1: int = 0
    u_v_l2: int = 0
    u_v_l3: int = 0
    iw_v_l1: int = 0
    iw_v_l2: int = 0
    iw_v_l3: int = 0
    ib_v_l1: int = 0
    ib_v_l2: int = 0
    ib_v_l3: int = 0
    is_v_l1: int = 0
    is_v_l2: int = 0
    is_v_l3: int = 0
    iw_pv_l1: int = 0
    iw_pv_l2: int = 0
    iw_pv_l3: int = 0
    ib_pv_l1: int = 0
    ib_pv_l2: int = 0
    ib_pv_l3: int = 0
    is_pv_l1: int = 0
    is_pv_l2: int = 0
    is_pv_l3: int = 0


@dataclass
class EnsData:
    f_netz: int = 0
    u_v_l1: int = 0
    u_v_l2: int = 0
    u_v_l3: int = 0


@dataclass
class ChargerData:
    # TODO
    pass


@dataclass
class BattData:
    # TODO
    pass


@dataclass
class EmsData:
    # /cgi/ems_datajs data
    wr_data: WrData | None = None
    emeter_data: EMeterData | None = None
    ens_data: EnsData | None = None
    charger_data: ChargerData | None = None
    batt_data: BattData | None = None
