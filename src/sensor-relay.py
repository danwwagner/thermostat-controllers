#!/usr/bin/env python

# Sensor Reading Author: Adafruit Foundation
# Source: https://learn.adafruit.com/adafruits-raspberry-pi-lesson-11-ds18b20-temperature-sensing/software
# Adapted and modified by: Dan Wagner
# Functionality added: GUI, multiple sensor readings, relay pins
# Agronomy Research, Summer 2018

import os
import glob
import time
import subprocess
import RPi.GPIO as GPIO
import codecs

# Adafruit MCP9808 library
import Adafruit_MCP9808.MCP9808 as mcp9808

# Filename for specific tent to write data
data_file = '01.txt'

# Temperature differential for tent
temperature_diff = 4

# Log file interval, in seconds
log_interval = 300

# Temperature checking interval, in seconds
check_interval = 60

# IP address of main server Pi
server_ip = '192.168.4.1'

# IP address of the control tent for outdoor temperature monitoring
control_ip = '192.168.4.2'

# List of sensors connected to the system
sensor_list = []

# Detect all MCP9808s connected to the system and set up the list to read them.
def detect_mcp9808():
    # Poll the number of sensors via text manipulation from the I2C bus.
    raw_sensors = subprocess.check_output("sudo i2cdetect -y 1 | sed 's/--//g' | tail -n +2 | sed 's/^.0://g' | sed 's/UU//g'", shell=True)

    # Holds the list of I2C addresses for each sensor
    addr_list = []

    # Name of an individual sensor
    sensor_name = ''

    # Create the sensor objects. 
    max = len(raw_sensors)
    for i in range(0, max):
        if raw_sensors[i] != ' ' and raw_sensors[i] != '\n':
            sensor_name += raw_sensors[i]
            if len(sensor_name) == 2:  # Hexadecimal addresses are two digits long
                addr_list.append(sensor_name)
                sensor_name = ''

    num_sensors = len(addr_list)

    # Begin communication with each sensor, and add it to the list of sensors.
    for i in range(0, num_sensors):
        sensor = mcp9808.MCP9808((int(addr_list[i], 16)))
        sensor.begin()
        sensor_list.append(sensor)     

    # Return the number of sensors connected
    return num_sensors
    
# Set up the relay signal pin
signal_pin = 17
# Use the Broadcom SOC channel number
GPIO.setmode(GPIO.BCM)
# Set it as an output pin
GPIO.setup(signal_pin, GPIO.OUT)
# Pull it low for safety
GPIO.output(signal_pin, GPIO.LOW)

# Initialize heater status to OFF
heater = "OFF"
# Counter to keep track of time elapsed before logging interval 
cnt = 0

# Delimit the next day's server connectivity via blank line
error_logs = codecs.open('connection.csv', 'a', 'utf-8')
error_logs.write('\n')
error_logs.close()

# Delimit the next day's individual sensor readings via blank line
sensor_readings = codecs.open('sensors.csv', 'a', 'utf-8')
sensor_readings.write('\n')
sensor_readings.close()

while True:
    # Initialize indoor temperature and delay time
    indoor = 0
    delay = 0
    bad_sensors = 0

    # Detect the sensors that are currently connected
    sensors = detect_mcp9808()
    
    try:
        # Open the sensor readings file and write the current timestamp.
        sensor_readings = codecs.open('sensors.csv', 'a', 'utf-8') 
        sensor_readings.write(time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()))
 
        # Read MCP9808 sensor data and log to file
        for i in range(0, sensors):
            temp = float(sensor_list[i].readTempC())
            sensor_readings.write("," + repr(temp))
            indoor += temp

        # Write a new line for the next reading interval
        sensor_readings.write('\n')
        
        # Close the sensor readings file
        sensor_readings.close()

        # Average the temperature readings for accuracy
        indoor /= (sensors - bad_sensors)

	# Round to three decimal places
        indoor = round(indoor, 3)

	# Retrieve the outdoor temperature from the control tent and parse it
        subprocess.call('scp pi@' + control_ip + ':/home/pi/outdoor .', shell=True)
		
        # Open the retrieved file, read the line, convert to floating point, and round to three decimal places
        outdoor = round(float(codecs.open('outdoor', 'r').read()), 3)
        if indoor == 0 and outdoor == 0: # both sensors disconnected while running, raise an exception
            raise RuntimeError
    except Exception as ex: # Exception occurred with sensor: notify via GUI
        indoor = 90
        outdoor = 90
        heater = "SENSOR"
        print ex
    
	# If the indoor temperature is below the differential, and no error has occurred, the heater is turned on
    if indoor - outdoor < temperature_diff and (indoor != 90 and outdoor != 90):
        GPIO.output(signal_pin, GPIO.HIGH)
        heater = "ON"
    else: # indoors hotter or equivalent temperature to outdoors -- turn off heater.
        GPIO.output(signal_pin, GPIO.LOW)
        if (indoor != 90 and outdoor != 90): heater = "OFF"

    # If log interval reached, record the timestamp, indoor and outdoor temperatures, and heater status to file
    if cnt == log_interval: # Log to file every 5 min (60s * 5 = 300s)
        output_file = codecs.open(data_file, 'w', 'utf-8')
        output_file.write(repr(indoor) + "," + repr(outdoor))
        output_file.close()

        # Attempt to copy the logs to the server Pi and log the error code (0 success, nonzero failure)
        error_logs = codecs.open('connection.csv', 'a', 'utf-8')
        error_code = subprocess.call('scp -o ConnectTimeout=30 /home/pi/' + data_file + ' pi@' + server_ip + ':/home/pi/Desktop', shell=True)
        error_logs.write(time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()) + "," + str(error_code) + "\n")
        error_logs.close()
        cnt = 0
    
    while delay < check_interval:
        # Top PiTFT button pressed -> shut the system down!
        time.sleep(0.5)
        delay += 0.5
    
    # Update the counter for the log interval timing
    cnt += check_interval
