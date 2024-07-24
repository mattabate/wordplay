#!/bin/bash

while true; do
    # Start the python script in the background
    python3 add_star.py &
    # Capture the process ID of the script
    PID=$!
    # Sleep for 30 seconds
    sleep 900
    # Kill the process
    kill $PID
    # Optional: Wait a moment before restarting the script
    sleep 2
done
