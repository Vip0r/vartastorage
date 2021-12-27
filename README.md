# Vartastorage
With this Python module you can read modbus registers and xml api values from various VARTA batteries. 
Tested on my VARTA element/12 battery.
Should work for other VARTA element, pulse, pulse neo, link and flex storage devices as well.

## Setup
pip3 install vartastorage

## Usage
```python
from vartastorage.vartastorage import VartaStorage

#ip and port for modbus host
varta = VartaStorage('10.0.2.3',502)

#update all values provided by modbus server
varta.get_all_data()

#show current grid power
print(varta.grid_power)

#update only SoC Value
varta.get_soc()

#show battery SoC
print(varta.soc)

```