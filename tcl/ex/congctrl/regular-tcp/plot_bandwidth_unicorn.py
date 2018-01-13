#!/usr/bin/env python3

import sys
import csv
import math

from plot_backend import plot_throughput

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

file_name = sys.argv[1]
try:
	number_of_senders = int(sys.argv[2])
except:
	eprint("Couldn't parse the number of senders, assuming 1.")
	number_of_senders = 1

values_to_plot = []
bins = []

for sender in range(number_of_senders):
	values_to_plot.append([])
	bins.append([])

with open(file_name, newline='') as csvfile:
	_ = csvfile.readline()
	csvreader = csv.reader(csvfile, delimiter=",")
	previous_value = [0] * number_of_senders
	for row in csvreader:
		# print("row", row)
		time = int(math.floor(float(row[0])))
		sender = int(row[1])
		current_value = int(row[2])

		bins[sender].append(time-1)
		values_to_plot[sender].append(current_value - previous_value[sender])
		previous_value[sender] = current_value

# Because units in remy are milliseconds for time and packets of 10000 bits each
values_to_plot = [[x/10 for x in item] for item in values_to_plot]
plot_throughput(bins, values_to_plot)
