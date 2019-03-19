from abc import ABCMeta, abstractmethod
import subprocess
import Adafruit_MCP9808.MCP9808 as mcp9808

# Include other subclasses for types of sensors to the end of the file
# This position is denoted by another comment


class Sensor(object):
    """
    Abstract base class for Sensor objects
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def __repr__(self):
        pass

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


class MCP9808(Sensor):
    """
     Subtype of Sensor class that implements MCP9808 sensor functionality.
    """

    def __init__(self):
        self.num_sensors = 0
        self.addr_list = []

    def __repr__(self):
        return "MCP9808"

    def num_sensors(self):
        """
        Retrieve the number of sensors detected
        """

        return self.num_sensors

    def detect(self):
        """
        Detects and internally records the number of
        MCP9808 connected to the system.
        Initializes each sensor for reading data.
        """

        # Command to detect the I2C bus connetions
        op = ("sudo i2cdetect -y 1 "
              "| sed 's/--//g' | tail -n +2 | "
              "sed 's/^.0://g' | sed 's/UU//g'")

        # Poll the number of sensors via text manipulation from the I2C bus.
        raw_sensors = subprocess.check_output(op, shell=True)

        # Holds the list of I2C addresses for each sensor
        self.addr_list = []

        # Hexcode of an individual sensor
        sensor_name = ''

        # Create the sensor objects.
        max = len(raw_sensors)
        for i in range(0, max):
            if raw_sensors[i] != ' ' and raw_sensors[i] != '\n':
                sensor_name += raw_sensors[i]
                if len(sensor_name) == 2:
                    # Hexadecimal addresses are two digits long
                    self.addr_list.append(sensor_name)
                    sensor_name = ''

        self.num_sensors = len(self.addr_list)

        # Begin communication with each sensor
        # and add it to the list.
        for i in range(0, self.num_sensors):
            sensor = mcp9808.MCP9808((int(self.addr_list[i], 16)))
            sensor.begin()
            self.sensor_list.append(sensor)

    def read(self):
        """
        Read sensor data and return the averaged value and each individual
        reading in CSV format for logging purposes.
        """

        indoor = 0
        sensor_readings = ""
        for i in range(0, self.num_sensors):
            temp = float(self.sensor_list[i].readTempC())
            sensor_readings += ("," + repr(temp))
            indoor += temp
        return indoor, sensor_readings

# Add other implementations of sensor types here
