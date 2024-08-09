#!/bin/bash

# Function to handle SIGINT (Ctrl+C)
trap 'echo "Exiting..."; kill $PID; exit 0;' SIGINT

while true; do
    # Start the python script in the background
    python3 main.py &
    # Capture the process ID of the script
    PID=$!
    # Print amount of time as string "timestep 3000"
    echo "timestep 3000"
    # Sleep for 180 seconds
    sleep 140
    # Kill the process
    kill $PID
    # Optional: Wait a moment before restarting the script
    sleep 1
done
