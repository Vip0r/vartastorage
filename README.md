# Vartastorage

With this Python module you can read modbus registers and xml api values from various VARTA batteries.
Tested on my VARTA element/12 battery.
Should work for other VARTA element, pulse, pulse neo, link and flex storage devices as well.

## Setup

pip3 install vartastorage

## Usage

```python
from vartastorage.vartastorage import VartaStorage

# ip and port for modbus host
varta = VartaStorage('10.0.2.3',502)

# in case of a password protected cgi/xml endpoint you can authenticate as well.
# user1 is for some varta devices a standard user
varta = VartaStorage('10.0.2.3', 502, username="user1", password="yourpassword")

# the CGI endpoints are covered by default. You can only use the modbus part as well
varta = VartaStorage("10.0.2.3", 502, cgi=False)

# update all values provided by modbus and HTTP
all_data = varta.get_all_data()

# update all values provided by modbus server
modbus_data = varta.get_all_data_modbus()

# show current grid power
print(modbus_data.grid_power)

# show battery SoC
print(modbus_data.soc)
```
