#!/bin/bash

echo "Starting Python scripts..."

# Activate virtual environment (modify path if needed)
source venv/bin/activate #for linux



# Run Python scripts in the background
python call.py &
python app.py &
python server.py &

echo "All scripts started!"
wait  # Ensures the script keeps running
