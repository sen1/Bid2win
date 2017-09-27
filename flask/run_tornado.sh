#!/bin/bash
SESSION=t1
tmux new-session -s $SESSION -n bash -d
tmux send-keys -t $SESSION 'sudo -E python tornadoapp.py' C-m
