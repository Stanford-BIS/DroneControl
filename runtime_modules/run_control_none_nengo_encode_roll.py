"""Forward input controls to output controls

run from terminal with
`python run_control_none_nengo_roll.py`
"""
from __future__ import print_function
import os
from dronestorm.comm.redis_util import DBRedis, REDIS_ATTITUDE_ROLL
import dronestorm.comm.redis_util as redis_util
from dronestorm.comm.rx_util import clip_rx
from dronestorm.print_util import print_control_header
from dronestorm.control.nengo_controllers import create_control_none_nengo_encode_roll
from dronestorm.nengo_util import run_nengo_realtime

def run_control_none_nengo_roll():
    """Function to forward the receiver signals to the control signals

    Reads receiver data from redis database
    sets command data to receiver data clipped to [-1, 1]
    Writes command data to redis database
    """
    print(os.path.basename(__file__))
    db_redis = DBRedis()
    nengo_sim, probe = create_control_none_nengo_encode_roll(sim_dt=0.005)

    print("Running control_none_nengo_roll...Ctrl-c to stop")
    print_control_header()
    run_nengo_realtime(nengo_sim, save_data={probe: "../data/nengo.log"})

if __name__ == "__main__":
    run_control_none_nengo_roll()
