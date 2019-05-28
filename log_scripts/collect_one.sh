#!/bin/sh
# Collects each heat tent's data and places it into the correct local directory
# Files and their meanings:
#  control.log: main Pythonic log file for system operation
#  sensors.csv: file of one-minute recordings of each temperature sensor value
#  {01,02,03}.txt: file of five-minute recordings of average temperature sensor value

# H1 Data
cd ~/Documents/research/agronomy/2019_testing/one
scp -vC pi@192.168.4.9:/home/pi/thermostat-controllers/src/\{control.log,sensors.csv,01.txt\} .

# C1 Data
cd ~/Documents/research/agronomy/2019_testing/one/control
scp -vC pi@192.168.4.1:/home/pi/thermostat-controllers/src/\{control.log,sensors.csv\} .
