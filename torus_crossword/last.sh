trap 'echo "Exiting..."; kill $PID; exit 0;' SIGINT

SLEEP_DURATION_GRID=$(python3 -c "import config; print(config.SLEEP_DURATION_GRID)")

# Check if SLEEP_DURATION_GRID is less than or equal to 0
if [ $SLEEP_DURATION_GRID -le 0 ]; then
    # Start the python script in the foreground and exit when done
    echo "Running search_filled.py"
    poetry run python3 search_filled.py
    exit 0
else
    while true; do
        echo "Starting new search_filled.py process"
        poetry run python3 search_filled.py &
        PID=$!
        
        # Wait for the script to finish or the timeout to expire
        TIMEOUT=$SLEEP_DURATION_GRID
        while [ $TIMEOUT -gt 0 ]; do
            sleep 1
            if ! kill -0 $PID 2>/dev/null; then
                echo "Process $PID finished before timeout"
                break
            fi
            ((TIMEOUT--))
        done
        
        if kill -0 $PID 2>/dev/null; then
            echo "Killing process $PID after $SLEEP_DURATION_GRID seconds"
            kill $PID
            sleep 1
        fi
        
        echo "Update Rate: $SLEEP_DURATION_GRID seconds"
    done
fi
