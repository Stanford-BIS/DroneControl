#!/bin/bash
# Script for running runtime_modules/run_control_yaw.py

TMUX_SESSION_NAME=run_control_yaw
CURDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
RUNDIR=${CURDIR}/../runtime_modules

tmux new-session -s ${TMUX_SESSION_NAME} -d "python ${RUNDIR}/run_drone_comm.py"
tmux split -v "python ${RUNDIR}/run_receiver.py"
tmux split -v "python ${RUNDIR}/run_control_yaw.py"
tmux select-layout -t ${TMUX_SESSION_NAME} even-vertical
tmux attach -t ${TMUX_SESSION_NAME}