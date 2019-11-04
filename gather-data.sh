#!/bin/bash


python bs4-example.py configs/schedule.config.json
python bs4-example.py configs/people.config.json



# cp candidates/time_schedule.json ../../public_html/generated/"time_schedule-$(date +%F_%R).json"
