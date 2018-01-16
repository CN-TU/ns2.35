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

for sender in range(number_of_senders):
	acked.append([])
	sent.append([])

with open(file_name, "r") as trace_file:
	lines = trace_file.readlines()

acked_regexes = []
sent_regexes = []
for sender in range(number_of_senders):
	acked_regexes.append(re.compile("^r -t (\d+\.?\d*).*\-s \d+ \-d "+str(sender)+" \-p ack.+\{.+ .+ (\d+) .+\}"))
	sent_regexes.append(re.compile("^\+ -t (\d+\.?\d*).*\-s "+str(sender)+" \-d \d+ \-p tcp -e (\d+).+\{.+ .+ (\d+) .+\}"))

for line in lines:

	for sender in range(number_of_senders):

		acked_match = acked_regexes[sender].search(line)
		# if acked_match is not None and int(acked_match.group(2)) >= 1:
		if acked_match is not None and int(acked_match.group(2)) >= 1:
			# acked[sender].append((int(acked_match.group(2)), float(acked_match.group(1))))
			acked[sender].append(int(acked_match.group(2)))

		sent_match = sent_regexes[sender].search(line)
		# first match is the time stamp second match is the packet size in bytes, third one the ack number,
		# if sent_match is not None and int(sent_match.group(3)) >= 1 and (len(sent[sender])==0 or int(sent_match.group(3)) > sent[sender][-1][0]):
		# if sent_match is not None and int(sent_match.group(3)) >= 1:
		if sent_match is not None and int(sent_match.group(3)) >= 1:
			sent[sender].append((int(sent_match.group(3)), int(sent_match.group(2)), float(sent_match.group(1))))

# print("acked", [item[:100] for item in acked])
# print("sent", [item[:100] for item in sent])

received = []
lost = []

for sender in range(number_of_senders):
	internal_acked = set(range(min(acked[sender]), max(acked[sender])+1))
	received.append([])
	lost.append([])

	# received[sender] = [item for item in sent[sender] if item[0] in acked[sender]]
	for i in reversed(range(len(sent[sender]))):
		seq_number, packet_size, time_stamp = sent[sender][i]
		# There's an ack that corresponds to this sent packet
		if seq_number in internal_acked:
			internal_acked.remove(seq_number)
			received[sender].append(sent[sender][i])
		# There's no ack for this packet. So it got lost!
		else:
			lost[sender].append(sent[sender][i])

	# only_ack_numbers = [item[0] for item in received[sender]]
	# Make sure than only_ack_numbers really only contains ints and that all ack numbers are unique;
	# no segment should be counted more than once.
	# assert(reduce(lambda acc, item: acc and item.__class__.__name__=="int", only_ack_numbers, True))
	# assert(len(only_ack_numbers) == len(set(only_ack_numbers)))
	received[sender] = list(reversed(received[sender]))
	lost[sender] = list(reversed(lost[sender]))

	# print("internal_acked", internal_acked)
	print("sender", sender, "len(sent)", len(sent[sender]), "len(received)", len(received[sender]))

# print("received", [item[:100] for item in received])
# print("lost", [item[:100] for item in lost])

# TIME_STEP = 0.03 # 30 ms

TIME_STEP = 0.1

# Things are expected to be an array with one entry for each sender. Each sender has an array of tuples,
# where each tuple contains a sequence number and a time stamp
def aggregation_function(things, number_of_senders):
	values_to_plot = []
	bins = []

	for sender in range(number_of_senders):
		values_to_plot.append([])
		bins.append([])
		prev_time_stamp = -TIME_STEP
		current_bin = -TIME_STEP
		# prev_thing_number = things[sender][0][0]-1
		# prev_thing_number = 0
		# for _, packet_size, time_stamp in received[sender]:
		for thing_number, packet_size, time_stamp in things[sender]:
			# Apparently this does happen...
			# assert(thing_number > prev_thing_number)
			# if not thing_number >= prev_thing_number:
			# 	print(prev_thing_number, thing_number)
			# assert(thing_number >= prev_thing_number)
			if prev_time_stamp < current_bin+TIME_STEP and time_stamp >= current_bin+TIME_STEP:
				# print("This actually happens")
				current_bin = math.floor(time_stamp/TIME_STEP)*TIME_STEP
				# print(current_bin)
				bins[sender].append(current_bin)
				# values_to_plot[sender].append(packet_size*(thing_number-prev_thing_number))
				values_to_plot[sender].append(packet_size)
			else:
				# values_to_plot[sender][len(bins[sender])-1] += (packet_size*(thing_number-prev_thing_number))
				values_to_plot[sender][len(bins[sender])-1] += packet_size

			# prev_thing_number = thing_number
			prev_time_stamp = time_stamp

		for index in range(len(values_to_plot[sender])):
			time_span = TIME_STEP
			if index < len(bins[sender]) - 1:
				time_span = bins[sender][index+1] - bins[sender][index]
			values_to_plot[sender][index] = values_to_plot[sender][index]*8/time_span/1e6

	return bins, values_to_plot

# print("doing received")
bins_received, values_to_plot_received = aggregation_function(received, number_of_senders)
# print("doing lost")
bins_lost, values_to_plot_lost = aggregation_function(lost, number_of_senders)

# if not bins_received == bins_lost:
# 	print(bins_received, bins_lost)

# assert(bins_received == bins_lost)

# print("bins", [item[:100] for item in bins])
# print("values_to_plot", [item[:100] for item in values_to_plot])

plot_throughput(bins_received, values_to_plot_received, bins_lost, values_to_plot_lost)
