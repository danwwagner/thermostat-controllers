import subprocess
import logging
# Adafruit MCP9808 library
#import Adafruit_MCP9808.MCP9808 as mcp9808

class MCP9808:

	# Initialize the number of sensors to 0
	def __init__(self):
		self.num_sensors = 0
		self.addr_list = []
		logging.basicConfig(filename='mcp9808.log', level=INFO)
		
	# Retrieve the number of sensors detected
	def num_sensors(self):
		return self.num_sensors

	# Attempts to detect connected MCP9808 sensors and returns True if successful, false otherwise.
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

		# Return the number of sensors connected
		if (self.num_sensors > 0):
			return True
		else:
			return False


	# Read sensor data and return the averaged value.
	def read(self):
		indoor = 0
		sensor_readings = 0
		for i in range(0, self.num_sensors):
			temp = float(self.sensor_list[i].readTempC())
			sensor_readings += ("," + repr(temp))
			indoor += temp
		return indoor, sensor_readings