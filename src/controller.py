#!/usr/bin/env python

# Sensor Reading Author: Adafruit Foundation
# Source: https://learn.adafruit.com/adafruits-raspberry-pi-lesson-11-ds18b20-temperature-sensing/software
# Adapted and modified by: Dan Wagner
# Functionality added: GUI, multiple sensor readings, relay pins
# Agronomy Research, Summer 2018
import logging
import sys
import time
#import RPi.GPIO as GPIO
import codecs
import subprocess

class Controller:

	# Initialize the variables in the system.
	def __init__(self, sensor_list):

		# Designate the type of sensor we are using.
		self.sensors = sensor_list

		# Keep track of the number of each type of sensors connected.
		self.num_sensors = [None] * len(self.sensors)

		# Filename for specific tent to write data
		self.data_file = '01.txt'

		# Format for logging information
		self.format="%(asctime)-15s %(message)s"

		# Temperature differential for tent
		self.temperature_diff = 4

		# Log file interval, in seconds
		self.log_interval = 300

		# Temperature checking interval, in seconds
		self.check_interval = 60

		# IP address of main server Pi
		self.server_ip = '192.168.4.1'

		# IP address of the control tent for self.outdoor temperature monitoring
		self.control_ip = '192.168.4.2'

		# List of sensors connected to the system
		self.sensor_list = []

		# Initialize the self.indoor temperature
		self.indoor = 0

		# Initialize the self.delay time period
		self.delay = 0
		
		# Initialize self.heater status to OFF
		self.heater = "OFF"
		
		# Initialize counter to keep track of time elapsed before logging interval 
		self.cnt = 0

		# Set up the relay signal pin
		self.signal_pin = 17

		# Use the Broadcom SOC channel number
		#GPIO.setmode(GPIO.BCM)
		
		# Set it as an output pin
		#GPIO.setup(self.signal_pin, GPIO.OUT)
		
		# Pull it low for safety
		#GPIO.output(self.signal_pin, GPIO.LOW)

		# Delimit the next day's server connectivity via blank line
		self.error_logs = codecs.open('connection.csv', 'a', 'utf-8')
		self.error_logs.write('\n')
		self.error_logs.close()

		# Delimit the next day's individual sensor readings via blank line
		self.sensor_readings = codecs.open('sensors.csv', 'a', 'utf-8')
		self.sensor_readings.write('\n')
		self.sensor_readings.close()

		# Instantiate the logging for debugging purposes
		self.logger = logging.getLogger("Controller")

	# Main loop of the program.
	def main(self):
		# Configure the logger and record the types of sensors that have been detected by the controller
		self.logger.basicConfig = logging.basicConfig(format=self.format, filename='controller.log',level=logging.INFO)
		self.logger.info('SYSTEM ONLINE')

		for sen in self.sensors:
			self.logger.info('Detected %s sensors', type(sen))

		while True:
			# Detect the sensors that are currently connected
			for i in range(0, len(self.sensors)):
				self.sensors[i].detect()
				self.num_sensors[i] = self.sensors[i].num_sensors

			try:
				# Open the sensor readings file and write the current timestamp.
				self.logger.info('Opening sensors file for records')
				self.sensor_readings = codecs.open('sensors.csv', 'a', 'utf-8') 
				self.sensor_readings.write(time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()))

				# Read sensor data from all types of connected sensors.
				self.logger.info('Reading sensors from Pi')
				total_indoor = 0
				total_readings = ""
				for sen in self.sensors:
					self.indoor, readings = sen.read()
					total_indoor += self.indoor
					total_readings += readings
				self.logger.info('Detected indoor temp of %d', total_indoor / len(self.sensors))

				# Log the individual readings.
				self.sensor_readings.write(total_readings)

				# Write a new line for the next reading interval
				self.sensor_readings.write('\n')
			
				# Close the sensor readings file
				self.sensor_readings.close()

				# Average the temperature readings for accuracy and type of sensors
				self.indoor = total_indoor / len(self.sensors)

				# Round to three decimal places
				self.indoor = round(self.indoor, 3)

				self.logger.info('Retrieving outdoor temperature from control tent')
				# Retrieve the self.outdoor temperature from the control tent and parse it
				subprocess.call('scp -o ConnectTimeout=10 pi@' + self.control_ip + ':/home/pi/outdoor .', shell=True)
				self.logger.info('Retrieved temperature: %d', self.indoor)

				# Open the retrieved file, read the line, convert to floating point, and round to three decimal places
				self.outdoor = round(float(codecs.open('self.outdoor', 'r').read()), 3)
				if self.indoor == 0 and self.outdoor == 0: # both sensors disconnected while running, raise an exception
					raise RuntimeError

			except Exception as ex: # Exception occurred with sensor: notify via GUI
				self.indoor = 90
				self.outdoor = 90
				self.heater = "SENSOR"
				# Record exception information
				
				self.logger.info('%s', repr(sys.exc_info()))
				print str(ex)

			# If the self.indoor temperature is below the differential, and no error has occurred, the self.heater is turned on
			if self.indoor - self.outdoor < self.temperature_diff and (self.indoor != 90 and self.outdoor != 90):
				#self.GPIO.output(self.signal_pin, GPIO.HIGH)
				self.heater = "ON"

			else: # self.indoors hotter or equivalent temperature to self.outdoors -- turn off self.heater.
				#self.GPIO.output(self.signal_pin, GPIO.LOW)
				if (self.indoor != 90 and self.outdoor != 90): 
					self.heater = "OFF"

			self.logger.info('%d inside, %d outside -- heater is %s', self.indoor, self.outdoor, self.heater)

			# If log interval reached, record the timestamp, self.indoor and self.outdoor temperatures, and self.heater status to file
			if self.cnt == self.log_interval: # Log to file every 5 min (60s * 5 = 300s)
				self.logger.info('Recording temperature data to tent file %s', self.data_file)
				self.output_file = codecs.open(self.data_file, 'w', 'utf-8')
				self.output_file.write(repr(self.indoor) + "," + repr(self.outdoor))
				self.output_file.close()

				self.logger.info('Recording connection data to connection.csv')
				# Attempt to copy the logs to the server Pi and log the error code (0 success, nonzero failure)
				self.error_logs = codecs.open('connection.csv', 'a', 'utf-8')
				error_code = subprocess.call('scp -o ConnectTimeout=30 /home/pi/' + self.data_file + ' pi@' + self.server_ip + ':/home/pi/Desktop', shell=True)
				self.logger.info('Error code received from SCP: %d', error_code)
				self.error_logs.write(time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()) + "," + str(error_code) + "\n")
				self.error_logs.close()
				self.cnt = 0

			# Sleep the system and increment self.delay
			while self.delay < self.check_interval:
				time.sleep(0.5)
				self.delay += 0.5

			# Update the counter for the log interval timing
			self.logger.info('Incrementing cnt (%d) by check_interval (%d)', self.cnt, self.check_interval)
			self.cnt += self.check_interval


# Begin the program
if __name__ == '__main__':
	# Each type of sensor (not number) is stored in this array
	sensors = [MCP9808()]
	c = Controller(sensors)
	c.main()