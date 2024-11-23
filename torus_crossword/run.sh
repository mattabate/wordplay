trap 'echo "Exiting..."; kill $PID; exit 0;' SIGINT

SLEEP_DURATION=$(python3 -c "import config; print(config.SLEEP_DURATION)")

# Check if SLEEP_DURATION is less than or equal to 0
if [ $SLEEP_DURATION -le 0 ]; then
    echo "running main.py"
    poetry run python3 main.py
    exit 0
else
    while true; do
        echo "Starting new running main.py process"
        poetry run python3 main.py &
        PID=$!
        
        # Wait for the script to finish or the timeout to expire
        TIMEOUT=$SLEEP_DURATION
        while [ $TIMEOUT -gt 0 ]; do
            sleep 1
            if ! kill -0 $PID 2>/dev/null; then
                echo "Process $PID finished before timeout"
                break
            fi
            ((TIMEOUT--))
        done
        
        if kill -0 $PID 2>/dev/null; then
            echo "Killing process $PID after $SLEEP_DURATION seconds"
            kill $PID
            sleep 1
        fi
        
        echo "Update Rate: $SLEEP_DURATION seconds"
    done
fi
