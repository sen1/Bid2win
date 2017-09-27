#!/bin/bash
SESSION=t1

#Create auction products
tmux new-session -s $SESSION -n bash -d
tmux send-keys -t $SESSION 'python kafka_auction_items.py ec2-34-234-250-83.compute-1.amazonaws.com' C-m


for i in `seq 2 3`;
do
   SESSION=t$i
   echo $SESSION
   tmux new-session -s $SESSION -n bash -d
   tmux send-keys -t $SESSION 'python kafka_generate_bids_v3.py ec2-34-235-37-82.compute-1.amazonaws.com' C-m
done   
