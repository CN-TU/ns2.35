#!/usr/bin/env python3

import os
import sys
import re
import plot_bandwidth_unicorn
import plot_backend
import numpy as np

all_file_names = list(map(lambda line: line[:-1], sys.stdin.readlines()))
# all_file_names = sys.argv[1:]
# print("all_file_names", all_file_names)

regexp = re.compile("^.*(\d+)_(\d+)_(.*)_(\d+)(?:_(.*))?\.0\.csv$")

parameter_to_results_dictionary = {}

for file_name in all_file_names:
	match = regexp.search(file_name)
	if match is None:
		continue
	# assert(match is not None)
	# key is "{sender_type}_{loss_type}"
	key = match.group(2)+"_"+match.group(1)
	if match.group(5) is not None and match.group(3) == match.group(5):
		key += "_again"
	# print("key", key)
	if not key in parameter_to_results_dictionary:
		parameter_to_results_dictionary[key] = []
	parameter_to_results_dictionary[key].append(list(map(lambda thing: np.array(thing), plot_bandwidth_unicorn.parse_file(file_name))))

print("Finished parsing all files, got the following keys:", parameter_to_results_dictionary.keys())
mean_and_std_dict_results = {}
mean_and_std_dict_lost = {}

sum_dict_results = {}
sum_dict_lost = {}

max_reference_length = 0

for key in sorted(parameter_to_results_dictionary.keys()):
	for run_array in parameter_to_results_dictionary[key]:
		for sender_array in run_array[0]:
			# print("sender_array", sender_array)
			reference_length = len(sender_array)
			max_reference_length = max(max_reference_length, reference_length)
		# assert(all(len(item[0]) == reference_length for item in all_stuff))

print("max_length", max_reference_length)

for key in sorted(parameter_to_results_dictionary.keys()):
	print(key)
	all_stuff = parameter_to_results_dictionary[key]
	flattened_throughput = [item for sublist in list(map(lambda item: item[1], all_stuff)) for item in sublist]
	for item in flattened_throughput:
		if len(item) < reference_length:
			print("len too small", len(item))
	too_small_indices = [index for index, x in enumerate(flattened_throughput) if len(x) < reference_length]
	for index in too_small_indices:
		del flattened_throughput[index]
	print("too_small_indices", too_small_indices)
	flattened_throughput = [np.append(item, np.zeros(reference_length-len(item))) for item in flattened_throughput]
	# print(list(map(lambda item: item.shape, flattened_throughput)))
	flattened_throughput = np.vstack(flattened_throughput)
	original_flattened_lost = [item for sublist in list(map(lambda item: item[2], all_stuff)) for item in sublist]
	for index in too_small_indices:
		del original_flattened_lost[index]
	original_flattened_lost = [np.append(item, np.zeros(reference_length-len(item))) for item in original_flattened_lost]
	# print(list(map(lambda item: item.shape, flattened_lost)))
	original_flattened_lost = np.vstack(original_flattened_lost)
	flattened_lost = (original_flattened_lost/(original_flattened_lost+flattened_throughput))
	flattened_lost[np.isnan(flattened_lost)] = 0.0
	print("Yeah", flattened_throughput.shape, flattened_lost.shape)
	mean_and_std_dict_results[key] = {"mean": np.mean(flattened_throughput, axis=0), "median": np.median(flattened_throughput, axis=0), "std": np.std(flattened_throughput, axis=0), "0.25": np.percentile(flattened_throughput, 25, axis=0), "0.75": np.percentile(flattened_throughput, 75, axis=0)}
	mean_and_std_dict_lost[key] = {"mean": np.mean(flattened_lost, axis=0), "median": np.median(flattened_lost, axis=0), "std": np.std(flattened_lost, axis=0), "0.25": np.percentile(flattened_lost, 25, axis=0), "0.75": np.percentile(flattened_lost, 75, axis=0)}
	sum_dict_results[key] = np.sum(flattened_throughput, axis=1)
	intermediate_lost = np.sum(original_flattened_lost, axis=1)
	sum_dict_lost[key] = intermediate_lost/(np.sum(flattened_throughput, axis=1)+intermediate_lost)
	print("Done")

file_name = all_file_names[0]
print("file_name", file_name)
last_slash = file_name.rfind("/")
actual_path = file_name[:last_slash+1]
last_part = file_name[last_slash+1:]
directory = actual_path + "figures"
if not os.path.exists(directory):
	os.makedirs(directory)

for key in sorted(parameter_to_results_dictionary.keys()):
	full_path = actual_path + "figures/" + key + ".png"
	plot_backend.plot_with_std(key, mean_and_std_dict_results[key], mean_and_std_dict_lost[key], output=full_path)
	# plot_backend.plot_with_std(key, mean_and_std_dict_results[key], mean_and_std_dict_lost[key])

plot_backend.plot_total_throughput(sorted(parameter_to_results_dictionary.keys()), sum_dict_results, sum_dict_lost)

print("Survived till here")