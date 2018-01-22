import matplotlib.pyplot as plt
import numpy as np

colors =  ["b", "g", "r", "c", "m", "y", "k", "w"]

def plot_throughput(bins, values_to_plot, values_to_plot_lost):
	number_of_senders = len(values_to_plot)

	for sender in range(number_of_senders):
		plt.subplot(1, 2, 1)

		plt.plot(np.array(bins[sender], dtype=np.float32), np.array(values_to_plot[sender], dtype=np.float32), colors[sender])
		plt.xlabel('time (s)')
		plt.ylabel('throughput (Mbit/s)')
		plt.legend(["throughput flow "+str(item) for item in range(1, number_of_senders+1)])

		plt.subplot(1, 2, 2)

		plt.xlabel('time (s)')
		# ax = plt.gca()
		# ax2 = ax.twinx()

		# ax.plot(np.array(bins[sender], dtype=np.float32), np.array(values_to_plot_lost[sender], dtype=np.float32), colors[sender]+"--")
		# ax.set_ylabel("lost throughput (Mbit/s)")
		# ax2.plot(np.array(bins[sender], dtype=np.float32), np.array(values_to_plot_lost[sender], dtype=np.float32)/(np.array(values_to_plot_lost[sender], dtype=np.float32)+np.array(values_to_plot[sender], dtype=np.float32)), colors[sender]+"-.")
		# ax2.set_ylabel("loss rate")

		# plt.plot(np.array(bins[sender], dtype=np.float32), np.array(values_to_plot_lost[sender], dtype=np.float32), colors[sender]+"--")
		plt.plot(np.array(bins[sender], dtype=np.float32), 100*np.array(values_to_plot_lost[sender], dtype=np.float32)/(np.array(values_to_plot_lost[sender], dtype=np.float32)+np.array(values_to_plot[sender], dtype=np.float32)), colors[sender]+"--")
		plt.ylabel("loss rate (%)")

		plt.legend(["loss rate of flow "+str(item) for item in range(1, number_of_senders+1)])

	plt.show()

HERD_COLOR = "k"
STD_COLOR = "0.5"
def plot_with_std(key, throughput, lost):

	plt.figure(key)
	plt.subplot(1, 2, 1)

	lines_throughput = plt.plot(list(range(throughput[0].shape[0])), throughput[0])
	plt.setp(lines_throughput, color=HERD_COLOR)
	space_throughput = plt.fill_between(list(range(throughput[0].shape[0])), throughput[0]-throughput[1], throughput[0]+throughput[1])
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

	lines_lost = plt.plot(list(range(lost[0].shape[0])), lost[0])
	plt.setp(lines_lost, color=HERD_COLOR)
	space_lost = plt.fill_between(list(range(lost[0].shape[0])), lost[0]-lost[1], lost[0]+lost[1])
	plt.setp(space_lost, color=STD_COLOR)
	# plt.plot(np.array(bins[sender], dtype=np.float32), 100*np.array(values_to_plot_lost[sender], dtype=np.float32)/(np.array(values_to_plot_lost[sender], dtype=np.float32)+np.array(values_to_plot[sender], dtype=np.float32)), colors[sender]+"--")
	plt.ylabel("loss rate (%)")

	plt.legend(["loss rate for "+key])

	plt.show()