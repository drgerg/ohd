#!/usr/bin/env python3

import os
import sys
import logging
import time
import signal
ohdHome = os.getcwd()

## GPIO setup
#
#GPIO.setwarnings(False)
#GPIO.setmode(GPIO.BCM)
#GPIO.setup(12, GPIO.IN, pull_up_down = GPIO.PUD_UP)
# GPIO.setup(24, GPIO.IN, pull_up_down = GPIO.PUD_UP)
# GPIO.setup(27, GPIO.IN, pull_up_down = GPIO.PUD_UP)
# GPIO.setup(23, GPIO.OUT)
# GPIO.setup(25, GPIO.OUT)
# GPIO.setup(21, GPIO.OUT)
# logger.debug("All them little GPIOs are set up")
#
## End GPIO setup

#PInStr = blinker.getPInStr()
#print(PInStr)
smtStartTime = time.strftime("%X",time.localtime())

print("smtStartTime: {}".format(smtStartTime))
