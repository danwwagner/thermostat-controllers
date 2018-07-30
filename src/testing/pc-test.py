#!/usr/bin/env python

# Author: Adafruit Foundation
# Modified by: Dan Wagner
# Functionality added: GUI, multiple sensor readings, relay pins
# 					logging interval, temperature interval 
# Agronomy Research, Summer 2018

from Tkinter import *
import tkFont
import glob
import time
import subprocess
import codecs
#import RPi.GPIO as GPIO

temperature_diff = 6
log_interval = 5
check_interval = 1
server_ip = '192.168.4.1'

# Credit for Python documentation for a good starting point for GUI
class Gui(Frame):
    def initialize(self):
        self.indoors = Button(self, text=(str(indoor)), font=bFont)
        #self.indoors.config(height=50, width=5)
        self.indoors.config(height=1, width=10)
        self.indoors.pack({"side": "top"})
        self.spacer = Button(self, text=heater, font=bFont)
        self.spacer.config(height=2, width=10)
        self.spacer.pack({"side": "top"})
        self.outdoors = Button(self, text=(str(outdoor)), font=bFont)
        #self.outdoors.config(height=50, width=5)
        self.outdoors.config(height=2, width=10)
        self.outdoors.pack({"side": "top"})

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.initialize()

# Gui features: courtesy of Python documentation
root = Tk()
bFont = tkFont.Font(root=root, family='Helvetica', size=70, weight='bold')
#root.geometry('%dx%d+%d+%d' % (480, 640, 0, 0))
root.attributes('-fullscreen', True)


#os.system('ip addr show')
sensor_list = []

def detect_sensors():

    # Probe the Pi's pins for the sensors
    #os.system('modprobe w1-gpio')
    #os.system('modprobe w1-therm')
    
    # Clear the list in case of errors previously
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
#signal_pin = 17
#GPIO.setmode(GPIO.BCM)
#GPIO.setup(signal_pin, GPIO.OUT)
#GPIO.output(signal_pin, GPIO.LOW)


# Set up the top pushbutton
#GPIO.setup(27, GPIO.IN, pull_up_down = GPIO.PUD_UP)

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


heater = "OFF"
cnt = 0

# Delimit the next day's reading via blank line
output_file = codecs.open('data.csv', 'a', 'utf-8')
output_file.write('\n')
output_file.close()

error_logs = codecs.open('connection.csv', 'a', 'utf-8')
error_logs.write('\n')
error_logs.close()

while True:
    delay = 0    
    # Top PiTFT button pressed -> shut the system down!
#    if not GPIO.input(27):
#        os.system('shutdown now')

    detect_sensors()
    # Read the temperature sensors
    try:
        indoor = read_temp(sensor_list[1])
        outdoor = read_temp(sensor_list[0])
        if indoor == 0 and outdoor == 0: # both sensors disconnected while running
            raise RuntimeError
    except: # Sensor not connected... 
        indoor = 90
        outdoor = 90
        heater = "SENSOR"
	#indoor = 30.125
	#outdoor = 34.567
    if indoor - outdoor < temperature_diff and (indoor != 90 and outdoor != 90):
#        GPIO.output(signal_pin, GPIO.HIGH)
        heater = "ON"
    else: # indoors hotter or equivalent temperature to outdoors -- turn off heater.
#        GPIO.output(signal_pin, GPIO.LOW)
		if indoor != 90 and outdoor != 90: heater = "OFF"

    gui = Gui(master=root)
    gui.update_idletasks()
    gui.update()

    if cnt == log_interval: # Log to file every 5 min (60s * 5 = 300s)
        output_file = codecs.open('data.csv', 'a', 'utf-8')
        output_file.write(time.strftime("%a %d %b %Y %H:%M:%S", time.localtime()) + "," +  repr(indoor) + "," + repr(outdoor) + "," + heater + "\n")
        output_file.close()

	# Attempt to copy the logs to the server Pi and log the error codes (0 success, nonzero failure)
        error_logs = codecs.open('connection.csv', 'a', 'utf-8')
        error_code = subprocess.call('scp -o ConnectTimeout=10 data.csv pi@' + server_ip + ':/home/pi/Desktop', shell=True)
        error_logs.write(time.strftime("%a %d %b %Y %H:%M:%S", time.localtime()) + "," + str(error_code) + "\n")
        error_logs.close()
        cnt = 0
    while delay < check_interval:
	    time.sleep(0.5)
	    delay += 0.5

    cnt += check_interval
    gui.destroy()
