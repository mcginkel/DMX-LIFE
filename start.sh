#!/bin/bash
# Start DMX Life application

# Navigate to the application directory
cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Start the application in the background
nohup python app.py > nohup.out 2>&1 &

# Get the PID
PID=$!
echo "DMX Life started with PID: $PID"
echo $PID > dmx_life.pid
echo "Server running at http://127.0.0.1:5050"
echo "To stop: kill \$(cat dmx_life.pid)"
