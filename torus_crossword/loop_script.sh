#!/bin/bash

while true; do
    # Start the python script in the background
    python3 add_star.py &
    # Capture the process ID of the script
    PID=$!
    # set timestep as variable
    # print ammount of time as string "timestep 1200"
    echo "timestep 30"
    # Sleep for 1200 seconds
    sleep 20
    # Kill the process
    kill $PID
    # Optional: Wait a moment before restarting the script
    sleep 1
done
