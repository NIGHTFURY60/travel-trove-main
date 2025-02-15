#!/bin/bash
python app.py &
python call.py &
python server.py &
pip install -r requirements.txt
wait
