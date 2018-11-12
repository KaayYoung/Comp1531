#!/bin/sh

virtualenv env && . env/bin/activate && pip3 install -r requirements.txt && python3 run.py -ld -q