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

    def __init__(self, reserved_addr):
        self.sensor_cnt = 0
        self.addr_list = []
        self.sensor_list = []
        self.changed_sensors = False
        self.reserved = list(reserved_addr)

    def __repr__(self):
        return "MCP9808"

    def num_sensors(self):
        """
        Retrieve the number of sensors detected
        """

        return self.sensor_cnt

    def detect(self):
        """
        Detects and internally records the number of
        MCP9808 connected to the system via i2c.
        Initializes each sensor for reading data.
        The code naively assumes that each i2c device
        is a sensor object; thus, ensure that the class
        list reserved has addresses that are used
        by i2c devices other than the MCP9808s.
        """

        # Command to detect the I2C bus connetions
        op = ("sudo i2cdetect -y 1 "
              "| sed 's/--//g' | tail -n +2 | "
              "sed 's/^.0://g' | sed 's/UU//g'")

        # Poll the number of sensors via text manipulation from the I2C bus.
        # raw_sensors = subprocess.check_output(op, shell=True)
        process = subprocess.Popen(op, stdout=subprocess.PIPE, shell=True)
        raw_sensors, _ = process.communicate()

        # Close the process/file
        # In this case, we ignore if it's already terminated/closed.
        try:
            process.terminate()
        except OSError:
            pass

        # Hexcode of an individual sensor
        sensor_name = ''
        temp_addr_list = []

        # Create the sensor objects.
        maxim = len(raw_sensors)
        for i in range(0, maxim):
            if raw_sensors[i] != ' ' and raw_sensors[i] != '\n':
                sensor_name += raw_sensors[i]
                if len(sensor_name) == 2 and sensor_name not in self.reserved:
                    # Hexadecimal addresses are two digits long
                    temp_addr_list.append(sensor_name)
                    sensor_name = ''

        # If a different number of sensors has been detected, update
        if (len(temp_addr_list) != len(self.addr_list)):
            for address in self.addr_list:
                del address
            for sensor in self.sensor_list:
                try:
                    del sensor
                except IndexError:
                    break
            del self.addr_list
            self.addr_list = list(temp_addr_list)
            self.changed_sensors = True

        self.sensor_cnt = len(self.addr_list)
        # Begin communication with each sensor
        # and add it to the list.
        i = 0
        for addr in self.addr_list:
            if self.changed_sensors:
                self.sensor_list.append(mcp9808.MCP9808((int(addr, 16))))
                try:
                    self.sensor_list[i].begin()
                except:
                    self.sensor_list.remove(self.sensor_list[i])
                    self.sensor_cnt -= 1
                    continue  # don't increment i
                i += 1

        self.changed_sensors = False

    def read(self):
        """
        Read sensor data and return the averaged value and each individual
        reading in CSV format for logging purposes.
        If a sensor goes offline between detection and read,
        then it is skipped.
        """

        indoor = 0
        sensor_readings = ""
        bad_sensors = 0
        for i in range(0, self.sensor_cnt):
            try:
                temp = float(self.sensor_list[i].readTempC())
            except:
                bad_sensors += 1
                continue # don't add to sensor_readings or indoor
            sensor_readings += ("," + repr(temp))
            indoor += temp
        indoor /= (self.sensor_cnt - bad_sensors)
        return indoor, sensor_readings

# Add other implementations of sensor types here
