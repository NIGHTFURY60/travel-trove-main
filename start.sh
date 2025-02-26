#!/bin/bash

echo "Starting Python scripts..."




# Run Python scripts in the background
gunicorn server:server &
gunicorn server:app &
gunicorn server:call &

echo "All scripts started!"
wait  # Ensures the script keeps running
