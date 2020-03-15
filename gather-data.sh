#!/bin/bash

# cd /home/grads/parasyris/thesis/csd-static-data-sources

# cd /home/grads/parasyris/thesis/csd-static-data-sources

cd /home/users/guest/groups/mobileapp/csd-data-gathering

python main.py

# python bs4-example.py configs/schedule.config.json
# python bs4-example.py configs/people.config.json


# cp candidates/time_schedule.json ../../public_html/generated/"time_schedule-$(date +%F_%R).json"
# cp candidates/time_schedule.json ../../public_html/generated/"people-$(date +%F_%R).json"

#cp -rf releases/ ../../public_html/releases/
rsync -a --delete releases/ ../public_html/releases/
rm -rf candidates/*.json


# python bs4-example.py configs/schedule.config.json
# python bs4-example.py configs/people.config.json



# cp candidates/time_schedule.json ../../public_html/generated/"time_schedule-$(date +%F_%R).json"
