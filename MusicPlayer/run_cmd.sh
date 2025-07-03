#!/bin/bash
source ./Venv/bin/activate
python main.py 2> >(grep -v "ALSA lib")
