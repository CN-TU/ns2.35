import matplotlib.pyplot as plt
import numpy as np

def plot_throughput(bins, values_to_plot, lost=None, overlapping=True):
	number_of_senders = len(values_to_plot)

	if not overlapping:
		fig, ax = plt.subplots(number_of_senders, sharex=True, squeeze=False)
		ax = ax.flatten()

		for sender in range(number_of_senders):
			ax[sender].plot(np.array(bins[sender], dtype=np.float32), np.array(values_to_plot[sender], dtype=np.float32))
			ax[sender].set(xlabel='time (s)', ylabel='throughput (Mbit/s)')
			# ax[sender].grid()

	else:
		for sender in range(number_of_senders):
			plt.plot(np.array(bins[sender], dtype=np.float32), np.array(values_to_plot[sender], dtype=np.float32))
			plt.xlabel('time (s)')
			plt.ylabel('throughput (Mbit/s)')
			# plt.grid()

	plt.show()