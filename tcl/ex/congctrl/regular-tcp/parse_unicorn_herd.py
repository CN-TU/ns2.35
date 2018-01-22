#!/usr/bin/env python3

import sys
import re
import plot_bandwidth_unicorn
import plot_backend
import numpy as np

all_file_names = list(map(lambda line: line[:-1], sys.stdin.readlines()))
# all_file_names = sys.argv[1:]
print("all_file_names", all_file_names)

regexp = re.compile("^.*(\d+)_(\d+)_.*_(\d+).0.csv$")

parameter_to_results_dictionary = {}

for file_name in all_file_names:
	match = regexp.search(file_name)
	assert(match is not None)
	# key is "{sender_type}_{loss_type}"
	key = str(match.group(2))+"_"+str(match.group(1))
	if not key in parameter_to_results_dictionary:
		parameter_to_results_dictionary[key] = []
	parameter_to_results_dictionary[key].append(list(map(lambda thing: np.array(thing), plot_bandwidth_unicorn.parse_file(file_name))))

print("Finished parsing all files, got the following keys:", parameter_to_results_dictionary.keys())
mean_and_std_dict_results = {}
mean_and_std_dict_lost = {}

for key in parameter_to_results_dictionary:
	print(key)
	all_stuff = parameter_to_results_dictionary[key]
	reference_length = len(all_stuff[0][0])
	assert(all(len(item[0]) == reference_length for item in all_stuff))
	flattened_throughput = [item for sublist in list(map(lambda item: item[1], all_stuff)) for item in sublist]
	# print(list(map(lambda item: item.shape, flattened_throughput)))
	flattened_throughput = np.vstack(flattened_throughput)
	flattened_lost = [item for sublist in list(map(lambda item: item[2], all_stuff)) for item in sublist]
	# print(list(map(lambda item: item.shape, flattened_lost)))
	flattened_lost = np.vstack(flattened_lost)
	flattened_lost = flattened_lost/(flattened_lost+flattened_throughput)
	print("Yeah", flattened_throughput.shape, flattened_lost.shape)
	mean_and_std_dict_results[key] = (np.mean(flattened_throughput, axis=0), np.std(flattened_throughput, axis=0))
	mean_and_std_dict_lost[key] = (np.mean(flattened_lost, axis=0), np.std(flattened_lost, axis=0))
	print("Done")

for key in sorted(parameter_to_results_dictionary.keys()):
	plot_backend.plot_with_std(key, mean_and_std_dict_results[key], mean_and_std_dict_lost[key])

print("Survived till here")