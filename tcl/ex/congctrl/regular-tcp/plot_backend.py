import matplotlib.pyplot as plt
import numpy as np

colors =  ["b", "g", "r", "c", "m", "y", "k", "w"]

def plot_throughput(bins, values_to_plot, bins_lost, values_to_plot_lost):
	number_of_senders = len(values_to_plot)

	for sender in range(number_of_senders):
		plt.plot(np.array(bins[sender], dtype=np.float32), np.array(values_to_plot[sender], dtype=np.float32), colors[sender])
		plt.xlabel('time (s)')
		plt.ylabel('rate (Mbit/s)')

		plt.plot(np.array(bins_lost[sender], dtype=np.float32), np.array(values_to_plot_lost[sender], dtype=np.float32), colors[sender]+"--")
		# plt.grid()

	plt.show()