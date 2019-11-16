#!/usr/bin/env python3

""" ohdpinchk.py - (OverHead Door) Check and return the status of the specified GPIO pin.
    2019 - Gregory Allen Sanders"""

import os
import sys
import logging
import time
import signal
import RPi.GPIO as GPIO

logger = logging.getLogger(__name__)

logger.debug("\nStart GPIO Setup")

## GPIO setup
#
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(12, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(24, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(27, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(25, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)
logger.debug("All them little GPIOs are set up")
#
## End GPIO setup

def main():

    logger.debug("Started the Main() function")
    time.sleep(1)
    logger.info("The door is " + pinChk() + ". Bypass is " + bpChk() +". Motion is " + pirChk())
    logger.debug("Finished the Main() function")


def pirChk():
    global pirStat
    if(GPIO.input(27) == False):
        pirStat = 'normal'
    else:
        pirStat = 'triggered'
    logger.debug("PIR: " + pirStat)
    return pirStat

def pinChk():
    global DoorStat
#    logger.debug("At top of pinChk()")
    if(GPIO.input(24) == False):
        DoorStat = 'closed'
        GPIO.output(25, GPIO.LOW)
    else:
        DoorStat = 'open'
        GPIO.output(25, GPIO.HIGH)
    logger.debug("Door: " + DoorStat)
    return DoorStat

def bpChk():
    global bpStat
#    logger.debug("At top of bpChk()")
    if(GPIO.input(12) == False):
        bpStat = 'On'
        GPIO.output(21, GPIO.HIGH)
    else:
        bpStat = 'Off'
        GPIO.output(21, GPIO.LOW)
    logger.debug("ByPass: " + bpStat)
    return bpStat


def SignalHandler(signal, frame):
        logger.info("Cleaning up . . . \n = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =")
        GPIO.cleanup()
        logger.debug("Finished GPIO.cleanup() in SignalHandler")
        logger.info("Shutting down gracefully")
        logger.debug("This is SignalHandler")
        logger.info("Displayed .info and .debug in SignalHandler")
        logger.info("Shutdown initiated")
        logger.debug("Wrote to log in SignalHandler")
        sys.exit(0)



if __name__ == "__main__":
    try:
        import argparse


        ## Command line arguments parsing
        #
        parserpc = argparse.ArgumentParser()
        parserpc.add_argument("-d", "--debug", help="Turn on debugging output to stderr", action="store_true")
        argspc = parserpc.parse_args()
        ohdHome = os.getcwd()
        if argspc.debug:
            logging.basicConfig(filename=ohdHome + '/ohd.log', format='[%(name)s]:%(levelname)s: %(message)s. - %(asctime)s', datefmt='%D %H:%M:%S', level=logging.DEBUG)
            logging.info("Debugging output enabled")
        else:
            logging.basicConfig(filename=ohdHome + '/ohd.log', format='%(asctime)s - %(message)s in %(name)s.', datefmt='%a, %d %b %Y %H:%M:%S', level=logging.INFO)
        #
        ## End Command line arguments parsing

        signal.signal(signal.SIGINT, SignalHandler)
        logger.debug("Top of try")
        while True:
            main()
        pass
        logger.info("Bottom of try")

    except:
        pass
        logger.info("That's all folks.  Goodbye")

