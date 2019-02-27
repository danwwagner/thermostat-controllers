from controller import Controller

# (1) Change sensor type here
from sensor import MCP9808

# (2) Change sensor type here
# List representation for use if the system will
# contain multiple types of temperature sensors.

# You must include a Python implementation that
# uses the Sensor superclass (see sensor.py)
sensor = [MCP9808()]

tent_control = Controller(sensor)
tent_control.main()
