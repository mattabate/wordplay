trap 'echo "Exiting..."; kill $PID; exit 0;' SIGINT

SLEEP_DURATION_GRID=$(python3 -c "import config; print(config.SLEEP_DURATION_GRID)")

# Check if SLEEP_DURATION is less than or equal to 0
if [ $SLEEP_DURATION_GRID -le 0 ]; then
    # Start the python script in the foreground and exit when done
    echo "running search_filled.py"
    poetry run python3 search_filled.py
    exit 0
else
    while true; do
        poetry run python3 search_filled.py &
        PID=$!
        echo "Update Rate: $SLEEP_DURATION_GRID"
        sleep $SLEEP_DURATION_GRID
        kill $PID
        sleep 1
    done
fi
