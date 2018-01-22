#!/usr/bin/env python3

import sys
import csv
import math

from plot_backend import plot_throughput

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def parse_file(file_name):

	values_to_plot = []
	lost = []
	bins = []

	unique_sender_ids = set()

	with open(file_name, newline='') as csvfile:
		_ = csvfile.readline()
		csvreader = csv.reader(csvfile, delimiter=",")

		for row in csvreader:
			unique_sender_ids.add(int(row[1]))

		number_of_senders = len(unique_sender_ids)

		for sender in range(number_of_senders):
			values_to_plot.append([])
			lost.append([])
			bins.append([])

		previous_value = [0] * number_of_senders
		previous_sent = [0] * number_of_senders

		csvfile.seek(0)
		_ = csvfile.readline()
		csvreader = csv.reader(csvfile, delimiter=",")
		for row in csvreader:
			# print("row", row)
			time = int(math.floor(float(row[0])))
			sender = int(row[1])
			current_value = int(row[2])
			current_sent = int(row[3])

			bins[sender].append(time-1)
			values_to_plot[sender].append(current_value - previous_value[sender])
			lost[sender].append((current_sent - previous_sent[sender]) - (current_value - previous_value[sender]))
			previous_value[sender] = current_value
			previous_sent[sender] = current_sent

		# Workaround that sometimes the lists are empty in the beginning.
		things_to_prepend = list(range(0,min(bins[sender])))
		bins[sender] = things_to_prepend + bins[sender]
		values_to_plot[sender] = ([0.0] * len(things_to_prepend)) + values_to_plot[sender]
		lost[sender] = ([0.0] * len(things_to_prepend)) + lost[sender]

		# lost[sender] = [lost_item/(lost_item+throughput_item) for throughput_item, lost_item in zip(values_to_plot[sender], lost[sender])]

	# Because units in remy are milliseconds for time and packets of 10000 bits each
	values_to_plot = [[x/100 for x in item] for item in values_to_plot]
	lost = [[x/100 for x in item] for item in lost]

	return bins, values_to_plot, lost

if __name__ == '__main__':
	file_name = sys.argv[1]
	bins, values_to_plot, lost = parse_file(file_name)
	# print(bins)
	plot_throughput(bins, values_to_plot, lost)
