#!/usr/bin/env python3

import sys
import re
import math

from plot_backend import plot_throughput

from functools import reduce

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def parse_file(file_name, number_of_senders):

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

	print("finished extraction")

	received = []
	lost = []

	largest_received_gap = 0
	largest_lost_gap = 0

	for sender in range(number_of_senders):
		# internal_acked = set(range(min(acked[sender]), max(acked[sender])+1))
		internal_acked = sorted(acked[sender])
		internal_ack_set = set(range(min(internal_acked), max(internal_acked)+1))
		assert(internal_acked == acked[sender])
		received.append([])
		lost.append([])

		# print("sent[sender]", sent[sender])
		# print("internal_acked", internal_acked)

		# received[sender] = [item for item in sent[sender] if item[0] in acked[sender]]
		# print(len(internal_acked))
		# largest_ack = internal_acked[-1]
		for i in reversed(range(len(sent[sender]))):
			seq_number, packet_size, time_stamp = sent[sender][i]
			# print(seq_number, end="")
			# There's an ack that corresponds to this sent packet
			if seq_number in internal_ack_set:
				# print(" r")
				# if not seq_number == largest_ack:
				# 	print(seq_number, largest_ack)
				# assert(seq_number == largest_ack)
				# largest_ack -= 1
				internal_ack_set.remove(seq_number)
				received[sender].append(sent[sender][i])

				if len(received[sender]) > 1:
					largest_received_gap = max(largest_received_gap, received[sender][-2][2] - received[sender][-1][2])
			# There's no ack for this packet. So it got lost!
			else:
				# print(" l")
				lost[sender].append(sent[sender][i])
				if len(lost[sender]) > 1:
					largest_lost_gap = max(largest_lost_gap, lost[sender][-2][2] - lost[sender][-1][2])

		assert(len(received[sender]) + len(lost[sender]) == len(sent[sender]))
		# print("largest_ack", largest_ack)
		# if not len(internal_acked) == 0:
		# 	print("internal_acked", internal_acked)
		# 	print("len(internal_acked)", len(internal_acked))
		# assert(len(internal_acked) == 0)

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
	print(largest_received_gap)
	print(largest_lost_gap)

	print("finished determining received and lost")

	# TIME_STEP = 2*largest_received_gap
	# TIME_STEP = largest_received_gap
	TIME_STEP = 0.1

	# Things are expected to be an array with one entry for each sender. Each sender has an array of tuples,
	# where each tuple contains a sequence number and a time stamp
	def aggregation_function(things, number_of_senders, lost=False):
		values_to_plot = []
		bins = []
		all_bins = []
		values_to_plot_final = []

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
				if not prev_time_stamp <= time_stamp:
					print(prev_time_stamp, time_stamp)
				assert(prev_time_stamp <= time_stamp)
				if prev_time_stamp < current_bin+TIME_STEP and time_stamp >= current_bin+TIME_STEP:
					# print("This actually happens")
					current_bin = math.floor(time_stamp/TIME_STEP)*TIME_STEP
					while len(bins[sender]) > 0 and round(bins[sender][-1]/TIME_STEP) < round((current_bin - TIME_STEP)/TIME_STEP):
						bins[sender].append(bins[sender][-1]+TIME_STEP)
						values_to_plot[sender].append(0.0)
					# print(current_bin)
					bins[sender].append(current_bin)
					# values_to_plot[sender].append(packet_size*(thing_number-prev_thing_number))
					values_to_plot[sender].append(packet_size)
				else:
					# values_to_plot[sender][len(bins[sender])-1] += (packet_size*(thing_number-prev_thing_number))
					values_to_plot[sender][len(bins[sender])-1] += packet_size

				# prev_thing_number = thing_number
				prev_time_stamp = time_stamp

			# print("bins", bins)

			for index in range(len(values_to_plot[sender])):
				time_span = TIME_STEP
				if index < len(bins[sender]) - 1:
					time_span = bins[sender][index+1] - bins[sender][index]
				print(time_span)
				values_to_plot[sender][index] = values_to_plot[sender][index]*8/time_span/1e6

			# print("values_to_plot", values_to_plot)
			# print("len(bins)", len(bins), "len(values_to_plot)", len(values_to_plot))

			all_bins.append(list([item*TIME_STEP for item in range(0, round(max(bins[sender])/TIME_STEP)+1)]))
			values_to_plot_final.append([0.0] * len(all_bins[sender]))

			print(len(values_to_plot[sender]))
			print(len(values_to_plot_final[sender]))
			for i in range(len(bins[sender])):
				index = round(bins[sender][i]/TIME_STEP)
				values_to_plot_final[sender][index] = values_to_plot[sender][i]

			# assert(reduce(lambda acc, x: x!=0 and acc, values_to_plot_final[sender], True))
			if not lost:
				if not len(bins[sender]) == len(all_bins[sender]):
					print(len(bins[sender]), len(all_bins[sender]))
				assert(len(bins[sender]) == len(all_bins[sender]))
				# assert(0.0 not in values_to_plot_final[sender])

		return all_bins, values_to_plot_final
		# return bins, values_to_plot

	print("finished binning")

	# print("doing received")
	bins_received, values_to_plot_received = aggregation_function(received, number_of_senders)
	# print("doing lost")
	bins_lost, values_to_plot_lost = aggregation_function(lost, number_of_senders, lost=True)

	# print(bins_received, bins_lost)
	TO_BE_DROPPED = 5

	for sender in range(number_of_senders):
		min_length = min(len(bins_received[sender]), len(bins_lost[sender]))
		bins_received[sender], values_to_plot_received[sender], bins_lost[sender], values_to_plot_lost[sender] = bins_received[sender][:min_length], values_to_plot_received[sender][:min_length], bins_lost[sender][:min_length], values_to_plot_lost[sender][:min_length]
		assert(len(bins_received[sender]) == round(max(bins_received[sender])/TIME_STEP) + 1)
		if not max(bins_lost[sender]) <= max(bins_received[sender]):
			print("something went wrong")
			print(len(bins_lost[sender]), len(bins_received[sender]))
			print(bins_lost[sender], bins_received[sender])
		assert(max(bins_lost[sender]) <= max(bins_received[sender]))
		assert(reduce(lambda acc, x: x != 0 and acc, values_to_plot_received, True))

		bins_received[sender], values_to_plot_received[sender], values_to_plot_lost[sender] = bins_received[sender][:-TO_BE_DROPPED], values_to_plot_received[sender][:-TO_BE_DROPPED], values_to_plot_lost[sender][:-TO_BE_DROPPED]

	return bins_received, values_to_plot_received, values_to_plot_lost

if __name__ == '__main__':
	file_name = sys.argv[1]

	try:
		number_of_senders = int(sys.argv[2])
	except:
		eprint("Couldn't parse the number of senders, assuming 1.")
		number_of_senders = 1

	bins_received, values_to_plot_received, values_to_plot_lost = parse_file(file_name, number_of_senders)
	plot_throughput(bins_received, values_to_plot_received, values_to_plot_lost)
