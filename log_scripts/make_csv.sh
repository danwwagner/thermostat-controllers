#!/bin/bash

# Runs the log parser and separates the data into three separate CSV files.
# These three files are then coalesced into a final file
# Argument list:
#  $1: Date of the experiment
#  $2: Time that H1 began recording data
#  $3: Time that H2 began recording data
#  $4: Time that H3 began recording data
#  $5: Coalesed data output file name

date=$1
h1Start=$2
h2Start=$3
h3Start=$4
outFile=$5

if [[ $# -lt 3 ]]; then
	echo "usage: $0 logDate h1StartTime h2StartTime h3StartTime outputFile"
	echo "For ease, you can specify a single start time and it will be used for all heat tents"
else	
	if [[ $# -ge 3 &&  "$#" -lt 5 ]]; then
		h2Start=$2
	 	h3Start=$2
		outFile=$3
	fi
	echo $date
	echo $h1Start
	echo $h2Start
	echo $h3Start
	echo $outFile	
	cd ~/Documents/research/agronomy/2019_testing/logs
	python3 parse_logs.py one/control.log one/sensors.csv tentOne.csv $date $h1Start
	python3 parse_logs.py two/control.log two/sensors.csv tentTwo.csv $date $h2Start
	python3 parse_logs.py three/control.log three/sensors.csv tentThree.csv $date $h3Start
	python3 coalesce_logs.py tentOne.csv tentTwo.csv tentThree.csv $outFile
fi
