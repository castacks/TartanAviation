#!/bin/bash

variable_one=$(df -h /dev/sda2)
variable_two=$(python /home/pi/ADS-B/garmin-virb/check_status.py)
variable_three=$(ps aux | grep python)

message="\{\"text\":\"Hello, World\n\"\}"

curl -X POST -H 'Content-type: application/json' --data '
{
        "text":"Current Data Status \n '"${variable_one}"' \n '"${variable_three}"' \n '"${variable_two}"'"
}' https://hooks.slack.com/services/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
