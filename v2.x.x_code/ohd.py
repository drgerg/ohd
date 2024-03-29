#!/usr/bin/env python3

""" ohd.py - (OverHead Door) is a complete re-write of my first completely useful Python utility.
My first project with a Raspberry Pi was intended to monitor a reed switch on my garage door,
and send me a text or email if it opened. That's not all it did, of course, but that's the gist.
It was finished in December of 2015, and ran flawlessly for three years.  The code was kludgy at best,
so I am re-writing it in an attempt to bring it more in line with good coding practices.  We shall see.
I am still an amateur.  Learning as I go, I started on this in January, 2019.  Finished it on 01/26/19.

June 2023: I still feel a touch of fondness toward this monolithic chunk of code.  It continues to do
its job flawlessly, and because of that, has earned the right to continue."""

import os
import sys
import configparser
import argparse
import logging
import time
import signal
import threading
import RPi.GPIO as GPIO
# import socket
import requests
import ohdpinchk
import ohdsendmail
import ohdreadmail
#
## Command line arguments parsing
#
parserohd = argparse.ArgumentParser()
parserohd.add_argument("-d", "--debug", help="Turn on debugging output to log file.", action="store_true")
parserohd.add_argument("-dd", "--ddebug", help="Turn on DEEP debugging output to log file.", action="store_true")
#
## Get the HOME environment variable
#
ohdHome = os.getcwd()
version = "v2.2.0"
#
## v2.2.0 - Adds camera recording when door is opened.
#
## ConfigParser init area.  Get some info out of working.conf.
#
config = configparser.ConfigParser()
config.read_file(open(ohdHome + '/ohd.conf'))
#
## End ConfigParser init
#
logger = logging.getLogger(__name__)
#
## End Logging Section
#
argsohd = parserohd.parse_args()

if argsohd.debug:
    import traceback
    logging.basicConfig(filename=ohdHome + '/ohd.log', format='[%(name)s]:%(levelname)s: %(message)s. - %(asctime)s', datefmt='%D %H:%M:%S', level=logging.DEBUG)
    logging.info("Debugging output enabled")
else:
    logging.basicConfig(filename=ohdHome + '/ohd.log', format='%(asctime)s - %(message)s', datefmt='%a, %d %b %Y %H:%M:%S', level=logging.INFO)
#
## End Command line arguments parsing

logger.info(" - - - - - - - ohd.py " + version + " INITIAL CONFIGURATION COMPLETE - - - - - - - - - - - ")
logger.info("'HOME' path is: " + ohdHome)
global DoorStat, bpStat, pirStat, pill2kill, Qtest, openFirst, bpFirst, tt, QmsgRcvdSent, bpLimit, bpLimNot
DoorStat = "closed"
bpStat = "Off"
pirStat = "normal"
Qtest = "[]"
QmsgRcvdSent = 0
bpLimit = config.getint('Notify', 'NotifyBPLimit')
bpLimNot = 0

def main():
    global DoorStat, bpStat, pill2kill, Qtest, openFirst, bpFirst, tt, QmsgRcvdSent, bpLimit, bpLimNot, mdMsgSent, tStart, pirStat, tFollow, tKill
    logger.info(" - - - - - - ohd.py " + version + " main() function NORMAL STARTUP  - - - - - - - - - - - - - ")
    tt = 60
    bpFirst = 0
    openFirst = 0
    mdMsgSent = 0
    ohdsendmail.msgS("ohd " + version + " Status Change", "Garage Door Monitor "+ version +" started normally at ")
    pill2kill = threading.Event()
    bpStatv = bpStat
    pt = threading.Thread(target=getPins, args=(pill2kill,bpStatv,))
    pt.start()
    PIRt = threading.Thread(target=getPIR, name="pirt", args=(pill2kill,))
    PIRt.start()
    if "Thread-1" in str(threading.enumerate()):
        pcT = "running"
    else:
        pcT = "not running"
    if "pirt" in str(threading.enumerate()):
        pirT = "running"
    else:
        pirT = "not running"
    logger.info("The getPins thread is " +  pcT)
    logger.info("The getPIR thread is " + pirT)

    while True:
#
## ByPass Off and Door CLOSED is the normal state.  Nothing needs to be done.
#
#
## ByPass OFF and Door OPEN - - this is the ALARM STATE
#
        if bpStat == 'Off' and DoorStat == 'open' and openFirst == 0:   # First time: Notify Door is OPEN
            camson()
            logger.info("ByPass is OFF and door is OPEN")
            openFirst = 1
            bpFirst = 0
            if Qtest != "Quiet":
                bpStatv = bpStat
                ohdsendmail.main(bpStatv)
            logger.debug("Starting the timer.")
            ttStart = time.time()                                              # Capture the time in ttStart


        elif bpStat == 'Off' and DoorStat == 'open' and openFirst == 1: # Subsequent times
            if time.time() - ttStart > tt and Qtest == "[]" and DoorStat == 'open':
                emAdd = config.get('CommandEmail', 'InBoundEmail1')
                Qtest, rmFrom, msgAuth = ohdreadmail.main()                     # Check for a Quiet message
                logger.info("ohdreadmail.main() returned Auth= " +msgAuth + "; "  + Qtest + ", From: " + rmFrom)
                if Qtest != 'Quiet':
                   logger.info("A minute has gone by.  Restarting time monitoring. Qtest = " + Qtest + ". Door is " + DoorStat)
                   bpStatv = bpStat
                   ohdsendmail.main(bpStatv)
                   Qtest = "[]"
                ttStart = time.time()
            else:
                if Qtest == "Quiet" and msgAuth == "Yes" and QmsgRcvdSent == 0:
                    ohdsendmail.msgS("Message Received", "A Quiet instruction was received from " + rmFrom + " at ") 
                    # the module function being called adds the timestamp.
                    QmsgRcvdSent = 1
#
## Turning ByPass ON while the Door is OPEN -- Notify once only
#
        if bpStat == 'On' and DoorStat == 'open':
            if bpFirst == 0:
                camsoff()
                logger.info("Door OPEN and ByPass ON" + ". bpFirst=" + str(bpFirst))
                bpStatv = bpStat
                ohdsendmail.main(bpStatv)
                bpFirst = 2         # '2' means the door is OPEN and ByPass is ON
                Qtest = "[]"
                QmsgRcvdSent = 0
                logger.info("bpFirst set to " + str(bpFirst))
                if argsohd.debug:
                    time.sleep(1)
            elif bpFirst == 1:
                logger.info("Door OPEN and ByPass ON. bpFirst=" + str(bpFirst) + ". Door was OPENED notification sent.")
                tSub = "Door Status Change"
                tMsg = "The door was OPENED while ByPass was On."
                ohdsendmail.msgS(tSub, tMsg)
                bpFirst = 2
                Qtest = "[]"
                QmsgRcvdSent = 0
                logger.info("bpFirst set to " + str(bpFirst))
                if argsohd.debug:
                    time.sleep(1)
#
## Turning ByPass ON for the first time while the door is CLOSED, OR closing the door WHILE ByPass is ON.
#
        if bpStat == 'On' and DoorStat == 'closed' and (bpFirst == 0 or bpFirst == 2):
            logger.info("ByPass is ON and door is CLOSED.  Sending notification.")
            if bpFirst == 2:
                openFirst = 0
            bpFirst = 1             # Set bpFirst after First ByPass On msg.  '1' means ByPass is ON and door is CLOSED
            Qtest = "[]"            # Reset Qtest
            QmsgRcvdSent = 0        # Reset Qmsg
            bpStatv = bpStatv
            camsoff()
            ohdsendmail.main(bpStatv)
            logger.info("bpFirst set to " + str(bpFirst))
            if argsohd.debug:
                time.sleep(1)

#
## Turning ByPass OFF while the door is closed.
#
        elif bpStat == 'Off' and DoorStat == 'closed' and bpFirst == 1:
            logger.info("ByPass was turned OFF")
            bpStatv = bpStat
            ohdsendmail.main(bpStatv)
            bpFirst = 0             # Reset bpFirst
            Qtest = "[]"            # Reset Qtest
            QmsgRcvdSent = 0        # Reset Qmsg
            bpLimNot = 0
            logger.info("bpFirst set to " + str(bpFirst))
            if argsohd.debug:
                time.sleep(1)
#
## ByPass OFF and Door CLOSED after having been OPEN - - notify it is closed now
#
        if bpStat == 'Off' and DoorStat == 'closed' and openFirst == 1:
            logger.info("Door Closed and ByPass OFF")
            bpStatv = bpStat
            ohdsendmail.main(bpStatv)
            if argsohd.debug:
                time.sleep(1)
            openFirst = 0
            bpFirst = 0
            camsoff()
            logger.info("bpFirst set to " + str(bpFirst))
#
## Check to see if ByPass was left on after hours.  If so, notify.  This relates to NotifyBPLimit in ohd.conf.
#
        locTime = time.localtime()
        if bpStat == "On" and locTime.tm_hour >= bpLimit and bpLimNot == 0:
            ohdsendmail.msgS("Late ByPass Notice", "It is after " + str(bpLimit) + "00, and Bypass is still On.")
            bpFirst = 1             # bpFirst = 1 means ByPass is ON and the door is CLOSED
            bpLimNot = 1            # set to 1 to prevent repeating messages about the time of day.

#
## Check the PIR Motion Detector's status.  This function starts video recording, then sends notifications.  It also spawns
## a threading.Timer() to run the motionDet function below which responds if the PIR is still triggered after the timer 
## has run down.
#
        if pirStat == 'triggered' and bpStat == 'Off' and (mdMsgSent == 0 or mdMsgSent == 2):
            mdDelay = config.get('MotionDetector', 'PirDelay')
            camRecLen = config.get('CamRecLength', 'recordtime')
            if mdMsgSent == 0:
                logger.info("pirStat is: " + pirStat + ". Bypass is: " + bpStat + ".  mdMsgSent is: " + str(mdMsgSent) + ". Starting Cams.")
                rangBell = ohdpinchk.bellRing()
                logger.info(rangBell)
                try:
                    requests.get('http://192.168.1.22:8090/command.cgi?cmd=record&tag=PIR%20tripped.')
                    smt = threading.Thread(target=ohdsendmail.msgS, args=("PIR", "The Front Porch motion detector was tripped "))
                    smt.start()
                    threadCount = threading.active_count()
                    logger.debug("threading.active_count is: " + str(threadCount))
                    logger.info("Motion detector was triggered. Camera recording started.")
                    mdMsgSent = 1
                    pirStat = 'normal'
                    logger.debug("The mdMsgSent variable was set to " + str(mdMsgSent))
                    mdt = threading.Timer(int(camRecLen), motionDet)
                    mdt.start()
                    mdtStartTime = time.strftime("%X",time.localtime())
                    logger.info("mdt Timer started at {}".format(mdtStartTime))
                    logger.debug("Started a threading.Timer. When it ends, the motionDet function will run.")
                except OSError:
                    logger.info('The security computer is non-responsive.  Setting the mdMsgSent variable to 0 anyway.')
                    mdMsgSent = 1
                    pirStat = 'normal'
                    logger.debug("Despite OSError, the mdMsgSent variable was set to " + str(mdMsgSent))
                    mdt = threading.Timer(int(camRecLen), motionDet)
                    mdt.start()
                    logger.debug("Started a threading.Timer. When it ends, the motionDet function will run.")
            if mdMsgSent == 2:
                mdt = threading.Timer(int(camRecLen), motionDet)
                mdt.start()
                threadCount = threading.active_count()
                logger.debug("threading.active_count is: " + str(threadCount))
                mdMsgSent = 3
#
## When something stops all this from being True, then we fall off the planet.
## I probably need do some exception catching stuff here . . .
#
    
    logger.info("Fell out of the Main() Function")
    log.flush()
#
##
### AUXILLIARY FUNCTIONS
##
#
## motionDet gets started as a thread when we have already sent one notification about 
## the PIR motion detector being tripped.  The function is started by the threading module
## as a thread, which means the main function can continue to loop while the timer is running down.
## Once the timer runs down (defined by the PirDelay setting in ohd.conf), this function is run.
#
def motionDet():
    global mdMsgSent, tStart, pirStat, tFollow, pill2kill, tKill
    mdtExecTime = time.strftime("%X",time.localtime())
    logger.info("motionDet function started at {}".format(mdtExecTime))
    logger.debug("Top of threaded motionDet. " + str(threading.currentThread()))
    if mdMsgSent == 3:
        mdMsgSent = 1
    if mdMsgSent == 2:
        mdMsgSent = 1
    if mdMsgSent == 1 and pirStat == 'normal' and bpStat == 'Off':
        logger.info("pirStat is: " + pirStat + ', and mdMsgSent is: ' + str(mdMsgSent) + '. (should be 1)')
        # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            requests.get('http://192.168.1.22:8090/command.cgi?cmd=recordStop')
            logger.info('Camera recording stopped by timer.')
            mdMsgSent = 0
        except OSError:
            logger.info('The security computer is non-responsive.  Setting the mdMsgSent variable to 0 anyway.')
            mdMsgSent = 0
    else:
        logger.info("pirStat is: {}. Bypass is {}.".format(pirStat,bpStat))
        requests.get('http://192.168.1.22:8090/command.cgi?cmd=recordStop')
        logger.info('Camera recording stopped. PIR or Bypass changed.')
        logger.debug("mdMsgSent: " + str(mdMsgSent) + ", setting to 2.")
        mdMsgSent = 2
        pass
#
## getPins is the function that gets started as a thread to continuously check the status of our triggers.
## This keeps the main function freed up and looping quickly, which enhances responsiveness.
#
def getPins(stop_event,bpStatv):
    global DoorStat, bpStat, pill2kill, Qtest, openFirst, bpFirst, tt

    while not stop_event.wait(1):
        DoorStat = ohdpinchk.pinChk()
        bpStatv = bpStat
        bpStat = ohdpinchk.bpChk(bpStatv)
        # pirStat = ohdpinchk.pirChk()
        # logger.info('From ohd.py, bpStat: ' + bpStat)
    else:
        logger.info("getPins dropped out")
        pass

def getPIR(stop_event):
    global pirStat, pill2kill
    # logger.info("top of getPIR")

    while not stop_event.wait(1):
        pirStat = ohdpinchk.pirChk()
        # logger.info(pirStat)
    else:
        logger.info("getPIR dropped out")
        pass

def camson():
    requests.get('http://192.168.1.22:8090/command.cgi?cmd=record&tag=PIR%20tripped.')
    logger.info('OHD opened. Camera recording started.')
    # smt = threading.Thread(target=ohdsendmail.msgS, args=("PIR", "The Front Porch motion detector was tripped "))

def camsoff():
    requests.get('http://192.168.1.22:8090/command.cgi?cmd=recordStop')
    logger.info('Camera recording stopped. OHD closed.')

def SignalHandler(signal, frame):
    global pill2kill
    print("SignalHandler invoked")
    pill2kill.set()
    logger.info(" - - - - - - - - - Cleaning up - - - - - - - - - - - - ")
    GPIO.cleanup()
    logger.debug("Finished GPIO.cleanup() in SignalHandler")
    logger.info("        Shutting down gracefully       ")
    ohdsendmail.msgS("ohd Status Change", "Shutdown Initiated")
    logger.debug("Sent 'Shutdown Now' message")
    logger.debug("Wrote to log in SignalHandler")
    # logger.info("Finished SignalHandler")
#        logger.flush()
#        logger.close()
    sys.exit(0)



if __name__ == "__main__":
    # global pill2kill
    import traceback
    try:
        signal.signal(signal.SIGINT, SignalHandler)  ## This one catches CTRL-C from the local keyboard
        signal.signal(signal.SIGTERM, SignalHandler) ## This one catches the Terminate signal from the system
        logger.info(" Top of try")
        while True:
            main()

    except Exception:
        pill2kill.set()
        error = traceback.print_exc()
        logger.debug(error)
        logger.info("That's all folks.  Goodbye")
