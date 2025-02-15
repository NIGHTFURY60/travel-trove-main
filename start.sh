#!/bin/bash
python app.py &
python call.py &
python server.py &
wait
