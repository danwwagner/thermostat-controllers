#!/usr/bin/env python

# Sensor Reading Author: Adafruit Foundation
# Source: https://learn.adafruit.com/adafruits-raspberry-pi-lesson-11-ds18b20-temperature-sensing/software
# Adapted and modified by: Dan Wagner
# Functionality added: GUI, multiple sensor readings, relay pins
# Agronomy Research, Summer 2018

from Tkinter import *
import tkFont
import os
import glob
import time
import subprocess
import RPi.GPIO as GPIO
import codecs

# Temperature differential for tent
temperature_diff = 6

# Log file interval, in seconds
log_interval = 300

# Temperature checking interval, in seconds
check_interval = 60


# Credit for Python documentation for a good starting point for GUI
class Gui(Frame):
    def initialize(self):
        # Top section of the GUI holds the indoor temperature
        self.indoors = Button(self, text=str(indoor), font=bFont)
        self.indoors.config(height=1, width=10)
        self.indoors.pack({"side": "top"})

        # Spacer section to make indoor and outdoor temperatures on top/bottom and look neat
        self.spacer = Button(self, text=heater, font=bFont)
        self.spacer.config(height=2, width=10)
        self.spacer.pack({"side": "top"})
		

        # Bottom section of the GUI holds the outdoor temperature
        self.outdoors = Button(self, text=str(outdoor), font=bFont)
        self.outdoors.config(height=2, width=10)
        self.outdoors.pack({"side": "top"})

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.initialize()

# Gui features: courtesy of Python documentation
root = Tk()

# Set the font on the GUI
bFont = tkFont.Font(root=root, family='Helvetica', size=70, weight='bold')

# Make the interface take up the entire screen
root.attributes('-fullscreen', True)

# List of sensors connected to the system
sensor_list = []

# Detect all sensors connected to the system and set up the list to read them.
def detect_sensors():
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

# Set up the relay signal pin
signal_pin = 17

# Use the Broadcom SOC channel number
GPIO.setmode(GPIO.BCM)

# Set it as an output pin
GPIO.setup(signal_pin, GPIO.OUT)

# Pull it low for safety
GPIO.output(signal_pin, GPIO.LOW)


# Set up the top pushbutton
GPIO.setup(27, GPIO.IN, pull_up_down = GPIO.PUD_UP)

# Open the file on the OS for the sensor data
def read_temp_raw(sensor):
    f = open(sensor, 'r')
    lines = f.readlines()
    f.close()
    return lines

# Read one of the temperature sensors and convert to meaningful data
def read_temp(sensor):
    lines = read_temp_raw(sensor)
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw(sensor)
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        #temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c #, temp_f

# Initialize heater status to off
heater = "OFF"

# Counter to keep track of time elapsed before logging interval
cnt = 0

# Delimit the next day's reading via blank line
output_file = codecs.open('data.csv', 'a', 'utf-8')
output_file.write('\n')
output_file.close()

while True:
    # Initialize delay time
    delay = 0

	# Detect the sensors connected
    detect_sensors()

    try:
        # Read the temperature sensors
        indoor = read_temp(sensor_list[0])
        outdoor = read_temp(sensor_list[1])
        if indoor == 0 and outdoor == 0:  # Sensor cannot be detected -- display on GUI
            raise RuntimeError
    except: # sensor not connected
        indoor = 90
        outdoor = 90
        heater = "SENSOR"

    	# If the indoor temperature is below the differential, and no error has occurred, the heater is turned on
    if indoor - outdoor < temperature_diff and (indoor != 90 and outdoor != 90):
        GPIO.output(signal_pin, GPIO.HIGH)
        heater = "ON"
    else: # indoors hotter or equivalent temperature to outdoors -- turn off heater.
        GPIO.output(signal_pin, GPIO.LOW)
        if indoor != 90 and outdoor != 90: heater = "OFF"

    # Update the GUI to represent the change in temperatures
    gui = Gui(master=root)
    gui.update_idletasks()
    gui.update()
    
    # If log interval reached, record the timestamp, indoor and outdoor temperatures, and heater status to file
    if cnt == log_interval: # Log to file every 5 min (60s * 5 = 300s)
        output_file = codecs.open('data.csv', 'a', 'utf-8')
        output_file.write(time.strftime("%a %d %b %Y %H:%M:%S", time.localtime()) + "," +  repr(indoor) + "," + repr(outdoor) + "," + heater + "\n")
        output_file.close()
        cnt = 0
    
    while delay < check_interval:
        # Top PiTFT button pressed -> shut the system down!
        if not GPIO.input(27):
            os.system('shutdown now')
        time.sleep(0.5)
        delay += 0.5
    
	# Update the counter for the log interval timing
    cnt += check_interval

	# Clean up resources for the next GUI update
    gui.destroy()
