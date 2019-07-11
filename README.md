# thermostat-controllers
Thermostat Controllers for Agronomy heat stress research

[![DOI](https://zenodo.org/badge/142898603.svg)](https://zenodo.org/badge/latestdoi/142898603) Version 1.0.0

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.1323816.svg)](https://doi.org/10.5281/zenodo.1323816) Version 2.0.0


[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3332925.svg)](https://doi.org/10.5281/zenodo.3332925) Version 3.0.0



This software constitutes a thermostat controller by reading attached temperature sensors and controlling a set of relays.  The system reads both the indoor and outdoor temperatures and measures their differential.  If the indoor temperature is not higher than the outdoor temperature by a defined amount, then a subset of the relays are activated to enable a heater to heat up the environment; the number of relays that come online are dependent upon the stage of the heater used.  Otherwise, the relays are deactivated and no heat is applied. If three consecutive remote I/O errors occur, then the system reboots and attempts to read again; this occurs until five reboots have happened, after which the system remains online for the remainder of the cycle. The number of errors and reboots can be changed within `controlcontroller.py` and `heatcontroller.py`.

## Versions
Version 1.0.0 supports two DS18B20 sensors attached.

Version 2.0.0 supports multiple DS18B20 sensors and implements wireless communication via an access point.

Version 3.0.0 supports multiple MCP9808 sensors and expands on the wireless communication by transferring outdoor/ambient temperatures to the heat tents instead of having the heat tents measure the temperature outside of themselves. Verbose log files were added for debugging and system health information. The MH_Z19 carbon dioxide sensor interfacing was implemented via Python module (see [this section](#mh_z19-python-module)). This version also ports the code over to Python 3.7.

## Repository Structure
This repository is organized into a single main folder: `src`. The main code that composes the thermostat controllers is located here and made up of four files: `main.py`, `sensor.py`, `controlcontroller.py` and `heatcontroller.py`; the latter two files are for control and heat tents respectively. The system's starting point lies within `main.py`, which initializes user-defined sensors and the specified controller (provided in the `sensor.py` and `heatcontroller.py`/`controlcontroller.py` files, respectively); any reserved I2C addresses must be specified here as the system assumes that all I2C devices (modulo an RTC module) are temperature sensors and will attempt to interface with them. If a control tent is using the software, then the ControlController lines in `main.py` should be uncommented and the HeatController lines should be commented out; the symmetric case is true for a heat tent. Interfaces, interactions, and implementations of sensor communication must be defined first in `sensor.py` if they are to be communicated with; the file must define a method of detecting sensors currently connected, a string representation for identifying the sensor's model, a method of keeping track of the number of sensors, and a way to read the data being transmitted from the sensors. The two controller files are the core of the system: each communicates via `sensor.py` implementations to monitor the temperature and depends on a wireless control tent setup to retrieve an ambient, outdoor temperature. This file will generate several files: a system health log (`control.log`), an aggregation of sensor readings (`sensors.csv`), and the retrieved outdoor ambient temperature (`outdoor`). The controller will monitor temperatures and initiate contact with relays; this version uses a Modine Mad-Dawg heater with two stages and three control lines (Call for Fan, Stage 1 Heat, Stage 2 Heat); control algorithms and electrical connectiosn for a specific heater will depend on manufacturer -- consult their documentation for assistance.

## Adafruit Python MCP9808
**See the repository link in the Acknowledgements.  Any folders or files mentioned are isolated to that repository.**

Python library for accessing the MCP9808 precision temperature sensor on a Raspberry Pi or Beaglebone Black.

Designed specifically to work with the Adafruit MCP9808 sensor ----> https://www.adafruit.com/product/1782

To install, first make sure some dependencies are available by running the following commands (on a Raspbian or Beaglebone Black Debian install):

````
sudo apt-get update
sudo apt-get install build-essential python-dev python-smbus
````

Then download the library by clicking the download zip link to the right and unzip the archive somewhere on your Raspberry Pi or Beaglebone Black. Then execute the following command in the directory of the library:

````
sudo python setup.py install
````

Make sure you have internet access on the device so it can download the required dependencies.

See examples of usage in the examples folder.

Adafruit invests time and resources providing this open source code, please support Adafruit and open-source hardware by purchasing products from Adafruit!

## MH_Z19 Python Module
Python module for interfacing with the MH_Z19 CO2 sensor. A separate implementation is not provided in `sensor.py` due to the simplicity of integration with this module.

Two versions can be installed: a full set, and only the sensor module.  For the full set, please see the repository link in the Acknowledgements.
To install the sensor module, run the following command:

````
sudo pip install mh-z19
````

After installation, the main.py file in the thermostat controller must be run with sudo privileges to access the serial bus correctly.
Installing with pip and excluding the sudo prefix may work for your system; however, if Python does not detect the library when running the script with sudo permissions then you must include the prefix.
## Acknowledgements
Thanks to Adafruit for their code for the DS18B20 and MCP9808 temperature sensors, and their installation guide above.

https://learn.adafruit.com/adafruits-raspberry-pi-lesson-11-ds18b20-temperature-sensing/overview

https://github.com/adafruit/Adafruit_Python_MCP9808 (courtesy of Tony DiCola, MIT license)

Thanks to UedaTakeyuki for their MH-Z19 Python module that made integration into the current system seamless.

https://github.com/UedaTakeyuki/mh-z19 (MIT license)

Author: Dan Wagner. MIT license, all text above must be included in any redistribution.
