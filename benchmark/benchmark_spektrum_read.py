# module for benchmarking spektrum calls
# benchmark the Spektrum protocol communication
from __future__ import print_function
import time
import timeit
import numpy as np
from dronestorm.comm import SpektrumRemoteReceiver

N = 100

print("Benchmarking Spektrum Remote Receiver read...")
print("Please ensure that:")
print("  - the remote receiver is connected properly to the pc")
print("  - the transmitter and receiver are bound")
print("  - the transmitter is on\n")
dt_read = np.zeros(N)
rrx = SpektrumRemoteReceiver()
rrx.align_serial()
for n in range(N):
    start = timeit.default_timer()
    rrx.read_data()
    dt_read[n] = timeit.default_timer()-start
mean_dt_read = np.mean(dt_read)
median_dt_read = np.median(dt_read)
std_dt_read = np.std(dt_read)

print("read mean:%5.2fms median:%5.2fms std:%5.2fms std/mean:%5.2f"%(
    mean_dt_read*1000, median_dt_read*1000,
    std_dt_read*1000, std_dt_read/mean_dt_read))
