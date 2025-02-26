#!/bin/bash

echo "Starting Python scripts..."




# Run Python scripts in the background
python call.py &
python app.py &
python server.py &

echo "All scripts started!"
wait  # Ensures the script keeps running
