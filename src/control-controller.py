#!/usr/bin/env python

# Sensor Reading Author: Adafruit Foundation
# Source: https://bit.ly/1iFB8ZP (DS18B20)
# Adapted and modified by: Dan Wagner
# Agronomy Research, 2018-2019

import logging
import sys
import time
import RPi.GPIO as GPIO
import codecs
import subprocess
import mh_z19


class Controller:
    """
    Controller class that manages the Thermostat system
    """
    def __init__(self, sensor_list):
        """
        Initializes the controller's variables and list of sensors.
        """

        # Designate the type of sensor we are using.
        self.sensors = sensor_list

        # Keep track of the number of each type of sensors connected.
        self.num_sensors = [None] * len(self.sensors)

        # Filename for specific tent to write data
        self.data_file = 'outdoor'

        # Format for logging information
        self.format = "%(asctime)-15s %(message)s"

        # Temperature differential for tent
        self.temperature_diff = 4

        # Log file interval, in seconds
        self.log_interval = 300

        # Temperature checking interval, in seconds
        self.check_interval = 60

        # List of sensors connected to the system
        self.sensor_list = []

        # Initialize the self.indoor temperature
        self.indoor = 0

        # Initialize the self.delay time period
        self.delay = 0

        # Initialize self.heater status to OFF
        self.heater = "OFF"

        # Initialize counter for time elapsed before logging interval
        self.cnt = 0

        # Set up the relay signal pin
        # self.signal_pin = 17

        # Use the Broadcom SOC channel number
        # GPIO.setmode(GPIO.BCM)

        # Set it as an output pin
        # GPIO.setup(self.signal_pin, GPIO.OUT)

        # Pull it low for safety
        # GPIO.output(self.signal_pin, GPIO.LOW)

        # Delimit the next day's individual sensor readings via blank line
        self.sensor_readings = codecs.open('sensors.csv', 'a', 'utf-8')
        self.sensor_readings.write('\n')
        self.sensor_readings.close()

        # Instantiate the logging for debugging purposes
        self.logger = logging.getLogger("Controller")

    # Main loop of the program.
    def main(self):

        """
        Configure the logger and record the types of
        sensors that have been detected by the controller.
        """

        self.logger.basicConfig = logging.basicConfig(format=self.format,
                                                      filename='control.log',
                                                      level=logging.INFO)

        self.logger.info('SYSTEM ONLINE')

        for sen in self.sensors:
            self.logger.info('Detected %s sensors', str(sen))

        mh_z19.zero_point_calibration()

        while True:
            # Detect the sensors that are currently connected
            for i in range(0, len(self.sensors)):
                self.sensors[i].detect()
                self.num_sensors[i] = self.sensors[i].num_sensors

            try:
                # Open the sensor readings file and write current timestamp.
                self.logger.info('Opening sensors file for records')
                self.sensor_readings = codecs.open('sensors.csv', 'a', 'utf-8')
                self.sensor_readings.write(time.strftime("%Y/%m/%d %H:%M:%S",
                                                         time.localtime()))

                # Read sensor data from all types of connected sensors.
                self.logger.info('Reading sensors from Pi')
                total_indoor = 0
                total_readings = ""
                for sen in self.sensors:
                    self.indoor, readings = sen.read()
                    total_indoor += self.indoor
                    total_readings += readings
                self.logger.info('Detected indoor temp of %.2f',
                                 total_indoor / len(self.sensors))

                # Log the individual readings.
                self.sensor_readings.write(total_readings)
                self.logger.info('Reading CO2 data')

                try:
                    # Read CO2 sensor data and log to file
                    co2_val = mh_z19.read()['co2']
                    fmt_string = "," + str(co2_val) + "ppm"
                    self.logger.info('Logging %d ppm to file', co2_val)
                    self.sensor_readings.write(fmt_string)
                except TypeError:
                    self.logger.info('Unable to read CO2 data')

                # Write a new line for the next reading interval
                self.sensor_readings.write('\n')

                # Close the sensor readings file
                self.sensor_readings.close()

                # Average temperature readings for accuracy
                self.indoor = total_indoor / len(self.sensors)

                # Round to three decimal places
                self.indoor = round(self.indoor, 3)

                if self.indoor == 0 and self.outdoor == 0:
                    # both sensors disconnected while running
                    raise RuntimeError

            except Exception as ex:
                # Exception occurred with sensor: notify via GUI
                self.indoor = 90
                self.outdoor = 90
                self.heater = "SENSOR"

                # Record exception information
                self.logger.info('%s', repr(sys.exc_info()))
                print str(ex)

	    # Immediately record outdoor temperature to file for control
            self.logger.info('Control: %d outside',self.indoor)

            self.logger.info('Recording temperature data to tent file %s',
                             self.data_file)
            if self.indoor != 90:
                self.output_file = codecs.open(self.data_file, 'w', 'utf-8')
                self.output_file.write(repr(self.indoor))
                self.output_file.close()
            else:
                self.logger.info('Cannot read sensors. Not logging to tent file.')

            time.sleep(self.check_interval)
