# Adapted and modified by: Dan Wagner
# Agronomy Research, 2018-2019

# CSV aggregation utility for HNT tents
# Consolidates the tent CSV files output from parse_logs.py
# Output file will contain one spreadsheet with multiple sheets.
# Each sheet corresponds to a heated tent's temperature and log data

import pandas
import argparse

# Get the files specified by the user
parser = argparse.ArgumentParser(description='Coalesces logs from' +
                                 'parse_logs.py into one single' +
                                 'Excel workbook with 3 sheets.')
parser.add_argument('tentOne', metavar='H1', type=str, nargs=1,
                    help='CSV of data for H1')
parser.add_argument('tentTwo', metavar='H2', type=str, nargs=1,
                    help='CSV of data for H2')
parser.add_argument('tentThree', metavar='H3', type=str, nargs=1,
                    help='CSV of data for H3')
# parser.add_argument('controlOne', metavar='H1', type=str, nargs=1,
#                    help='CSV of data for C1')
# parser.add_argument('controlTwo', metavar='C2', type=str, nargs=1,
#                    help='CSV of data for C2')
# parser.add_argument('controlThree', metavar='C3', type=str, nargs=1,
#                    help='CSV of data for C3')
parser.add_argument('output', metavar='outputFile', type=str, nargs=1,
                    help='Output file for coalesced data')

# Parse the arguments
args = parser.parse_args()
first = args.tentOne[0]
second = args.tentTwo[0]
third = args.tentThree[0]
# cfirst = args.controlOne[0]
# csecond = args.controlTwo[0]
# cthird = args.controlThree[0]
output = args.output[0]

# Credit for adapted code to consolidate CSVs
# https://bit.ly/2YRechv

# Set up overall writing object
writer = pandas.ExcelWriter(output, engine='xlsxwriter')

# Reac in each CSV and place it as a sheet in the output file
file_1 = pandas.read_csv(first)
file_1.to_excel(writer, sheet_name='H1.csv', index=False)
# file_4 = pandas.read_csv(cfirst)
# file_4.to_excel(writer, sheet_name='C1.csv', index=False)
file_2 = pandas.read_csv(second)
file_2.to_excel(writer, sheet_name='H2.csv', index=False)

file_3 = pandas.read_csv(third)
file_3.to_excel(writer, sheet_name='H3.csv', index=False)

# Write to output
writer.save()
