from controller import Controller

# (1) Change sensor type here
from sensor import MCP9808

# (2) Change sensor type here
# List representation for use if the system will
# contain multiple types of temperature sensors.


# List of reserved i2c addresses
# that are used by components
# other than temperature sensors.
# Make sure that each of the elements
# in this list are hexadecimal strings
# i.e. "0x1A".
reserved = [""]

# You must include a Python implementation that
# uses the Sensor superclass for the
# type of sensor in your system (see sensor.py)
sensor = [MCP9808(reserved)]

# Initialize the controller program
tent_control = Controller(sensor, reserved)

# Enter the main control loop
tent_control.main()
