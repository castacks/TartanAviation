#!/bin/bash

#sh ./mount_disk.sh
#mkdir -p /media/storage/vid/`date -I`
#kill $(pgrep -f 'getcamera.py')
#/usr/bin/python -u /home/pi/ADS-B/garmin-virb/delete_all.py > /home/pi/ADS-B/del.log &
/usr/bin/python -u /home/pi/adsb_recorder/run_recorder.py > /home/pi/adsb_recorder/flight.log &
#/usr/bin/python -u /home/pi/ADS-B/scripts/getcamera.py > /home/pi/ADS-B/camera.log &
#nohup autossh -M 20002 -N -R 20000:localhost:22 jaypat@perceptron.ri.cmu.edui
#/usr/bin/python -u /home/pi/ADS-B/scripts/wall.py >> /home/pi/ADS-B/haha.log 2>&1
