#!/bin/bash
# Start DMX Life application

# Navigate to the application directory
cd "$(dirname "$0")"

# Load local credentials/overrides if present. .env is gitignored; see
# .env.example for the variables it can set (DMXLIFE_USERNAME,
# DMXLIFE_PASSWORD, DMXLIFE_HOST, DMXLIFE_DEBUG).
if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

# Bind to all interfaces so devices on the venue network can reach the UI.
# This is what makes DMXLIFE_USERNAME/DMXLIFE_PASSWORD required below.
export DMXLIFE_HOST="${DMXLIFE_HOST:-0.0.0.0}"

# Activate virtual environment
source venv/bin/activate

# Start the application in the background
nohup python app.py > nohup.out 2>&1 &

# Get the PID
PID=$!
echo $PID > dmx_life.pid

# The app can refuse to start (missing credentials, debug on a network bind)
# and exit almost immediately. Check for that rather than reporting success
# regardless.
sleep 1
if ! ps -p $PID > /dev/null 2>&1; then
    echo "DMX Life failed to start. Log output:"
    echo "---"
    tail -n 20 nohup.out
    echo "---"
    rm -f dmx_life.pid
    exit 1
fi

echo "DMX Life started with PID: $PID"
echo "Server running at http://${DMXLIFE_HOST}:5050"
echo "To stop: kill \$(cat dmx_life.pid)"
