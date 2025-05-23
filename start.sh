#!/bin/bash
# Start DMX Life application

# Navigate to the application directory
cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Start the application
python app.py
