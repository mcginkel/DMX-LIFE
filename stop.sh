#!/bin/bash
# Stop DMX Life application

# Navigate to the application directory
cd "$(dirname "$0")"

# Check if PID file exists
if [ ! -f dmx_life.pid ]; then
    echo "Error: dmx_life.pid not found. Is the server running?"
    exit 1
fi

# Read the PID
PID=$(cat dmx_life.pid)

# Check if process is running
if ! ps -p $PID > /dev/null 2>&1; then
    echo "Error: Process $PID is not running"
    rm -f dmx_life.pid
    exit 1
fi

# Kill the process
echo "Stopping DMX Life (PID: $PID)..."
kill $PID

# Wait a moment for graceful shutdown
sleep 1

# Check if process is still running
if ps -p $PID > /dev/null 2>&1; then
    echo "Process still running, forcing kill..."
    kill -9 $PID
    sleep 1
fi

# Verify it's stopped
if ps -p $PID > /dev/null 2>&1; then
    echo "Error: Failed to stop process $PID"
    exit 1
else
    echo "DMX Life stopped successfully"
    rm -f dmx_life.pid
fi
