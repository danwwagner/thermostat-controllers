# parse_logs.py
# Author: Dan Wagner
# Agronomy Research, HNT project: 2018-2019

# Parser for logfiles from HNT tents.
# Provided with valid arguments, this code outputs a CSV with the following:
#   1. Relative timestamp of when each line of data was logged
#   2. Indoor sensor readings (labeled Sensor#1, Sensor#2, etc.)
#   3. Average of the indoor sensor readings in (2)
#   4. Outdoor sensor reading received from the control tent
#   5. Heater status

import argparse
import os
from datetime import datetime, timedelta

# Get the files specified by the user
parser = argparse.ArgumentParser(description='Process tent logs to one CSV.' +
                                 ' Files are assumed to be located in'
                                 ' subdirectories of this file\'s working' +
                                 ' directory within the filesystem.')
parser.add_argument('syslog', metavar='control.log', type=str, nargs=1,
                    help='System log file from the tent')
parser.add_argument('sensors', metavar='sensors.csv', type=str, nargs=1,
                    help='CSV file of tent temperature readings')
parser.add_argument('output', metavar='out_file', type=str, nargs=1,
                    help='Output file to write data')
parser.add_argument('date', metavar='log_date', type=str, nargs=1,
                    help='Calendar date for recent log data (mm/dd/yyyy)')
parser.add_argument('start', metavar='start_time', type=str, nargs=1,
                    help='Start time for data collection')
# parser.add_argument('end', metavar='end_time', type=str, nargs=1,
#                    help='Ending time for data collection')
args = parser.parse_args()


# Set directory of arguments w.r.t. current directory
cwd = os.getcwd() + '/'
out_file = cwd + args.output[0]
control_log = cwd + args.syslog[0]
sensor_file = cwd + args.sensors[0]


# Set up date information
start_time = args.start[0].split(':')
hour = int(start_time[0])
minute = int(start_time[1])

timestamp = args.date[0].split('/')
timestamp = datetime(int(timestamp[2]), int(timestamp[0]),
                     int(timestamp[1]), hour, minute)


# Set up output file column data formatting
sensor_interval = timedelta(seconds=62)


# Set up sensor file data (readings start, file contents, num sensors)
readings_line = 0
lines_array = []
num_sensors = 0


# Read file into memory (< 30 KB)
with open(sensor_file, 'rb') as s:
    lines_array = s.readlines()

# Find the newline that denotes the most recent readings and
# start reading the file at that point
for num, line in enumerate(lines_array, 0):
    line = line.split(b'\x00')
    if '/' not in line[0].decode():
        readings_line = num + 1
print('New reading in sensors.csv starts at %d' % readings_line)
lines_array = lines_array[readings_line:]

# Get timestamp that correlates with control.log information
starting_line = lines_array[0].decode().split(',')
start_timestamp = starting_line[0].split(',')[0].split(':')[0]
start_timestamp += ":" + starting_line[0].split(':')[1]
start_timestamp = start_timestamp.replace("/", "-")

# Get number of temperature sensors and their data
num_sensors = len(starting_line[2:]) + 1
print('Found values for %d sensors' % num_sensors)
temperatures_list = []
for entry in lines_array:
    sensor_data = entry.decode().split('\n')[0].split(',')[1:]
    sense_read = ""
    avg = 0
    for val in sensor_data:
        sense_read += str(val) + ','
        avg += float(val)
    sense_read += str(round(avg / num_sensors, 2))
    temperatures_list.append(sense_read)

# Retrieve control log information (outdoor temp, heater status)
control_lines = []
ctrl_list = []
i = -1
control_reading = 0
flag = 0  # prevents duplicate log files/readings
with open(control_log, 'r') as c:
    control_lines = c.readlines()
for num, line in enumerate(control_lines, 0):
    if 'SYSTEM ONLINE' in line:
        control_reading = num + 1
print('New reading in control.log starts at line %d' % (control_reading))
control_lines = control_lines[control_reading:]
for line in control_lines:
    if 'Retrieved' in line:
        line = line.split('temperature:')
        ctrl_list.append(line[1].strip())
        i += 1
        flag = 0
    elif 'heater' in line and flag == 0:
        line = line.split(',')
        ctrl_list[i] += ',' + line[3].split('heater')[1].strip() + '\n'
        flag = 1

# Create the header
header = 'Timestamp'
for i in range(1, num_sensors + 1):
    header += ',Sensor#' + str(i)
header += ',Heat,Control,Heater'

# Create the output file
with open(out_file, 'w') as f:
    print(header)
    f.write(header + '\n')
    max_num = min(len(temperatures_list), len(ctrl_list))
    for i in range(0, max_num):
        out_line = str(timestamp)
        out_line += ',' + temperatures_list[i]
        out_line += ',' + ctrl_list[i]
        timestamp += sensor_interval
        f.write(out_line)
