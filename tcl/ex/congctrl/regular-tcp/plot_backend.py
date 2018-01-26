import matplotlib.pyplot as plt
import numpy as np

colors =  ["b", "g", "r", "c", "m", "y", "k", "w"]

LINE_WIDTH = 0.75
HERD_COLOR = "k"
STD_COLOR = "0.5"

def plot_throughput(bins, values_to_plot, values_to_plot_lost, output=None):
	plt.figure()

	number_of_senders = len(values_to_plot)

	for sender in range(number_of_senders):
		plt.subplot(1, 2, 1)

		plt.plot(np.array(bins[sender], dtype=np.float32), np.array(values_to_plot[sender], dtype=np.float32), colors[sender], linewidth=LINE_WIDTH)
		plt.xlabel('time (s)')
		plt.ylabel('throughput (Mbit/s)')
		plt.legend(["flow "+str(item) for item in range(1, number_of_senders+1)])

		plt.subplot(1, 2, 2)

		plt.xlabel('time (s)')
		# ax = plt.gca()
		# ax2 = ax.twinx()

		# ax.plot(np.array(bins[sender], dtype=np.float32), np.array(values_to_plot_lost[sender], dtype=np.float32), colors[sender]+"--")
		# ax.set_ylabel("lost throughput (Mbit/s)")
		# ax2.plot(np.array(bins[sender], dtype=np.float32), np.array(values_to_plot_lost[sender], dtype=np.float32)/(np.array(values_to_plot_lost[sender], dtype=np.float32)+np.array(values_to_plot[sender], dtype=np.float32)), colors[sender]+"-.")
		# ax2.set_ylabel("loss rate")

		# plt.plot(np.array(bins[sender], dtype=np.float32), np.array(values_to_plot_lost[sender], dtype=np.float32), colors[sender]+"--")
		y = 100*np.array(values_to_plot_lost[sender], dtype=np.float32)/(np.array(values_to_plot_lost[sender], dtype=np.float32)+np.array(values_to_plot[sender], dtype=np.float32))
		y[np.isnan(y)] = 0.0
		plt.plot(np.array(bins[sender], dtype=np.float32), y, colors[sender], linewidth=LINE_WIDTH)
		plt.ylabel("loss rate (%)")

		plt.legend(["flow "+str(item) for item in range(1, number_of_senders+1)])

	show_or_save_plot(output)

def show_or_save_plot(output):
	plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0.3, hspace=None)
	plt.tight_layout()
	if output is None:
		plt.show()
	else:
		plt.savefig(output)

def plot_with_std(key, throughput, lost, output=None):

	plt.figure()
	plt.subplot(1, 2, 1)

	# print("throughput", throughput)
	# print("lost", lost)

	lines_throughput = plt.plot(list(range(throughput["median"].shape[0])), throughput["median"])
	plt.setp(lines_throughput, color=HERD_COLOR)
	space_throughput = plt.fill_between(list(range(throughput["median"].shape[0])), throughput["0.25"], throughput["0.75"])
	plt.setp(space_throughput, color=STD_COLOR)
	plt.xlabel('time (s)')
	plt.ylabel('throughput (Mbit/s)')
	plt.legend(["throughput for "+key])

	plt.subplot(1, 2, 2)

	plt.xlabel('time (s)')
	# ax = plt.gca()
	# ax2 = ax.twinx()

	# ax.plot(np.array(bins[sender], dtype=np.float32), np.array(values_to_plot_lost[sender], dtype=np.float32), colors[sender]+"--")
	# ax.set_ylabel("lost throughput (Mbit/s)")
	# ax2.plot(np.array(bins[sender], dtype=np.float32), np.array(values_to_plot_lost[sender], dtype=np.float32)/(np.array(values_to_plot_lost[sender], dtype=np.float32)+np.array(values_to_plot[sender], dtype=np.float32)), colors[sender]+"-.")
	# ax2.set_ylabel("loss rate")

	lost = {key: value*100 for key, value in zip(lost.keys(), lost.values())}
	lines_lost = plt.plot(list(range(lost["median"].shape[0])), lost["median"])
	plt.setp(lines_lost, color=HERD_COLOR)
	space_lost = plt.fill_between(list(range(lost["median"].shape[0])), lost["0.25"], lost["0.75"])
	plt.setp(space_lost, color=STD_COLOR)
	# plt.plot(np.array(bins[sender], dtype=np.float32), 100*np.array(values_to_plot_lost[sender], dtype=np.float32)/(np.array(values_to_plot_lost[sender], dtype=np.float32)+np.array(values_to_plot[sender], dtype=np.float32)), colors[sender]+"--")
	plt.ylabel("loss rate (%)")

	plt.legend(["loss rate for "+key])

	show_or_save_plot(output)

def plot_total_throughput(keys, throughput_sums, lost_sums, output=None):

	plt.figure()
	plt.subplot(1, 2, 1)

	plt.boxplot([throughput_sums[item] for item in keys])
	plt.xticks(range(1, len(keys)+1), keys)

	plt.subplot(1, 2, 2)

	plt.boxplot([lost_sums[item]*100 for item in keys])
	plt.xticks(range(1, len(keys)+1), keys)

	# fig, ax1 = plt.subplots()
	# ax2 = ax1.twinx()

	# N = 5
	# print("keys", keys)
	# print("throughput_sums", throughput_sums)
	# throughput_means = [np.mean(throughput_sums[item]) for item in keys]
	# throughput_stds = [np.std(throughput_sums[item]) for item in keys]

	# lost_means = [np.mean(lost_sums[item])*100 for item in keys]
	# lost_stds = [np.std(lost_sums[item])*100 for item in keys]

	# ind = np.arange(len(keys))

	# width = 0.35

	# # print("throughput_means", throughput_means)
	# # print("throughput_stds", throughput_stds)
	# throughput_plot = ax1.bar(ind, throughput_means, width=width, color='r', yerr=throughput_stds)
	# lost_plot = ax2.bar(ind + width, lost_means, width=width, color='b', yerr=lost_means)

	# ax1.set_xticks(ind + width / 2)
	# ax1.set_xticklabels(keys)

	# # add some text for labels, title and axes ticks
	# # plt.set_ylabel('Scores')
	# # plt.set_title('Throughput and loss rate')
	# # plt.set_xticks(ind + width / 2)
	# # plt.set_xticklabels(keys)

	# # plt.legend((rects1[0], rects2[0]), ('Throughput', 'Loss rate'))

	show_or_save_plot(output)
