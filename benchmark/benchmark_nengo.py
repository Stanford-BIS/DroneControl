# benchmark nengo simulator
import time
import nengo
import numpy as np

net = nengo.Network()
with net:
    stim = nengo.Node(lambda t: np.sin(t))
    ens = nengo.Ensemble(100, 1)
    out = nengo.Node(lambda t, x: x)
    nengo.Connection(stim, ens)
    nengo.Connection(ens, out, function=lambda x:x**2)

sim = nengo.Simulator(net)
print(sim.dt)