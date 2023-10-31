#!/bin/bash

#sh ./mount_disk.sh
#mkdir -p /media/storage/vid/`date -I`
/usr/bin/python -u /home/pi/adsb_audio_recorder/scripts/run_adsb_audio.py > /home/pi/adsb_audio_recorder/ADSB.log &
