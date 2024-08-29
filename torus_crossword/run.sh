# Define the sleep duration in seconds
SLEEP_DURATION=600

trap 'echo "Exiting..."; kill $PID; exit 0;' SIGINT

# Check if SLEEP_DURATION is less than or equal to 0
if [ $SLEEP_DURATION -le 0 ]; then
    # Start the python script in the foreground and exit when done
    echo "running main.py"
    poetry run python3 main.py
    exit 0
else
    while true; do
        # Start the python script in the background
        poetry run python3 main.py &
        # Capture the process ID of the script
        PID=$!
        # Print amount of time as string "timestep <SLEEP_DURATION>"
        echo "timestep $SLEEP_DURATION"
        # Sleep for SLEEP_DURATION seconds
        sleep $SLEEP_DURATION
        # Kill the process
        kill $PID
        # Optional: Wait a moment before restarting the script
        sleep 1
    done
fi
