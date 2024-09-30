trap 'echo "Exiting..."; kill $PID; exit 0;' SIGINT

SLEEP_DURATION=$(python3 -c "import config; print(config.SLEEP_DURATION)")

# Check if SLEEP_DURATION is less than or equal to 0
if [ $SLEEP_DURATION -le 0 ]; then
    # Start the python script in the foreground and exit when done
    echo "running main.py"
    poetry run python3 main.py
    exit 0
else
    while true; do
        poetry run python3 main.py &
        PID=$!
        echo "timestep $SLEEP_DURATION"
        sleep $SLEEP_DURATION
        kill $PID
        sleep 1
    done
fi
