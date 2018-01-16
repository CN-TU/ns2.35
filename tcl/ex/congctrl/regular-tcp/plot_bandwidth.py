#!/usr/bin/env python3

import sys
import re
import math

from plot_backend import plot_throughput

from functools import reduce

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

file_name = sys.argv[1]
try:
	number_of_senders = int(sys.argv[2])
except:
	eprint("Couldn't parse the number of senders, assuming 1.")
	number_of_senders = 1

acked = []
sent = []

PACKET_SIZE = 1250

for sender in range(number_of_senders):
	acked.append([])
	sent.append([])

with open(file_name, "r") as trace_file:
	lines = trace_file.readlines()

acked_regexes = []
sent_regexes = []
for sender in range(number_of_senders):
	acked_regexes.append(re.compile("^r.*\-s \d+ \-d "+str(sender)+" \-p ack.+\{.+ .+ (\d+) .+\}"))
	sent_regexes.append(re.compile("^\+ -t (\d+\.?\d*).*\-s "+str(sender)+" \-d \d+ \-p tcp -e (\d+).+\{.+ .+ (\d+) .+\}"))

for line in lines:

	for sender in range(number_of_senders):

		acked_match = acked_regexes[sender].search(line)
		if acked_match is not None and int(acked_match.group(1)) >= 1:
			acked[sender].append(int(acked_match.group(1)))

		sent_match = sent_regexes[sender].search(line)
		# first match is the time stamp second match is the packet size in bytes, third one the ack number,
		if sent_match is not None and int(sent_match.group(3)) >= 1 and (len(sent[sender])==0 or int(sent_match.group(3)) > sent[sender][-1][0]):
			sent[sender].append((int(sent_match.group(3)), int(sent_match.group(2)), float(sent_match.group(1))))

# print("acked", [item[:100] for item in acked])
# print("sent", [item[:100] for item in sent])

received = []

for sender in range(number_of_senders):
	acked[sender] = set(acked[sender])
	received.append([])
	received[sender] = [item for item in sent[sender] if item[0] in acked[sender]]
	only_ack_numbers = [item[0] for item in received[sender]]
	# Make sure than only_ack_numbers really only contains ints and that all ack numbers are unique;
	# no segment should be counted more than once.
	assert(reduce(lambda acc, item: acc and item.__class__.__name__=="int", only_ack_numbers, True))
	assert(len(only_ack_numbers) == len(set(only_ack_numbers)))
	print("sender", sender, "len(sent)", len(sent[sender]), "len(received)", len(received[sender]))

# print("received", [item[:100] for item in received])

values_to_plot = []
bins = []

# TIME_STEP = 0.03 # 30 ms
TIME_STEP = 0.1
for sender in range(number_of_senders):
	values_to_plot.append([])
	bins.append([])
	prev_time_stamp = -TIME_STEP
	current_bin = -TIME_STEP
	for _, packet_size, time_stamp in received[sender]:
		if prev_time_stamp < current_bin+TIME_STEP and time_stamp >= current_bin+TIME_STEP:
			# print("This actually happens")
			current_bin = math.floor(time_stamp/TIME_STEP)*TIME_STEP
			# print(current_bin)
			bins[sender].append(current_bin)
			values_to_plot[sender].append(packet_size)
		else:
			values_to_plot[sender][len(bins[sender])-1] += packet_size
		prev_time_stamp = time_stamp

	for index in range(len(values_to_plot[sender])):
		time_span = TIME_STEP
		if index < len(bins[sender]) - 1:
			time_span = bins[sender][index+1] - bins[sender][index]
		values_to_plot[sender][index] = values_to_plot[sender][index]*8/time_span/1e6

# print("values_to_plot", [item[:100] for item in values_to_plot])
# print("bins", [item[:100] for item in bins])

plot_throughput(bins, values_to_plot)
