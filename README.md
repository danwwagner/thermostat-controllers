# thermostat-controllers
Thermostat Controllers for Agronomy heat stress research

[![DOI](https://zenodo.org/badge/142898603.svg)](https://zenodo.org/badge/latestdoi/142898603) Version 1.0.0

This software constitutes a thermostat controller by reading attached temperature sensors and controlling a set of relays.  The system reads both the indoor and outdoor temperatures and measures their differential.  If the indoor temperature is not higher than the outdoor temperature by a coded amount, then the relays are activated to enable a heater to heat up the environment.  Otherwise, the relays are deactivated and no heat is applied.

## Versions
Version 1.0.0 supports two DS18B20 sensors attached.

Version 2.0.0 supports multiple DS18B20 sensors and implements wireless communication via an access point.

## Adafruit Python MCP9808
See the repository link in the description.  Any folders or files mentioned are isolated to that repository.

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

## Acknowledgements
Thanks to Adafruit for their code for the DS18B20 and MCP9808 temperature sensors.
https://learn.adafruit.com/adafruits-raspberry-pi-lesson-11-ds18b20-temperature-sensing/overview

https://github.com/adafruit/Adafruit_Python_MCP9808 (courtesy of Tony DiCola, MIT license)

Author: Dan Wagner. MIT license, all text above must be included in any redistribution.
