from abc import ABCMeta, abstractmethod
import subprocess
#import Adafruit_MCP9808.MCP9808 as mcp9808

# Include other subclasses for types of sensors to the end of the file
# This position is denoted by another comment

# Abstract base class for Sensor objects
class Sensor(object):
	__metaclass__ = ABCMeta

	@abstractmethod
	def __init__(self):
		pass

	@abstractmethod
	def num_sensors(self):
		pass

	@abstractmethod
	def detect(self):
		pass

	@abstractmethod
	def read(self):
		pass

# Subclass for MCP9808
class MCP9808(Sensor):

	# Initialize class variables
	def __init__(self):
		self.num_sensors = 0
		self.addr_list = []
		
	# Retrieve the number of sensors detected
	def num_sensors(self):
		return self.num_sensors

	# Attempts to detect connected MCP9808 sensors.
	def detect(self):
		# Poll the number of sensors via text manipulation from the I2C bus.
		raw_sensors = subprocess.check_output("sudo i2cdetect -y 1 | sed 's/--//g' | tail -n +2 | sed 's/^.0://g' | sed 's/UU//g'", shell=True)

		# Holds the list of I2C addresses for each sensor
		self.addr_list = []

		# Hexcode of an individual sensor
		sensor_name = ''

		# Create the sensor objects. 
		max = len(raw_sensors)
		for i in range(0, max):
			if raw_sensors[i] != ' ' and raw_sensors[i] != '\n':
				sensor_name += raw_sensors[i]
				if len(sensor_name) == 2:  # Hexadecimal addresses are two digits long
					addr_list.append(sensor_name)
					sensor_name = ''

		self.num_sensors = len(self.addr_list)

		# Begin communication with each sensor, and add it to the list of sensors.
		for i in range(0, self.num_sensors):
			sensor = mcp9808.MCP9808((int(self.addr_list[i], 16)))
			sensor.begin()
			self.sensor_list.append(sensor) 

	# Read sensor data and return the averaged value.
	def read(self):
		indoor = 0
		sensor_readings = ""
		for i in range(0, self.num_sensors):
			temp = float(self.sensor_list[i].readTempC())
			sensor_readings += ("," + repr(temp))
			indoor += temp
		return indoor, sensor_readings

# Add other implementations of sensor types here
class DS18B20(Sensor):
	import os
	import glob

	def __init__(self):
		self.num_sensors = 0
		self.sensor_list = []

	# Retrieve the number of sensors detected
	def num_sensors(self):
		return self.num_sensors

	# Detect all DS18B20s connected to the system and set up the list to read them.
	def detect(self):

		# Probe the Pi's pins for the sensors
		os.system('modprobe w1-gpio')
		os.system('modprobe w1-therm')

		# Clear the list in case of previous errors
		sensor_list[:] = []

		# Retrieve the sensors' directories (default directory followed by 28-xxxx)
		base_dir = '/sys/bus/w1/devices/'
		sensor_dir = glob.glob(base_dir + '28*')

		# Get the number of DS18B20 sensors
		num_sensors = len(sensor_dir)

		# Add each file to a list of sensors
		for i in range(0, num_sensors):
			sensor_list.append(sensor_dir[i] + '/w1_slave')

	# Read each sensor's data and convert to meanginful data.
	# Adapted from Adafruit
	def read(self):
		temp_c = 0
		for sensor in self.sensor_list:
			lines = read_temp_raw(sensor)
			while lines[0].strip()[-3:] != 'YES':
				time.sleep(0.2)
				lines = read_temp_raw(sensor)
			equals_pos = lines[1].find('t=')
			if equals_pos != -1:
				temp_string = lines[1][equals_pos+2:]
				temp_c += float(temp_string) / 1000.0
		return temp_c


	# Open the file for the DS18B20 on the OS for the sensor data
	# Courtesy of Adafruit
	def read_temp_raw(sensor):
		f = open(sensor, 'r')
		lines = f.readlines()
		f.close()
		return lines