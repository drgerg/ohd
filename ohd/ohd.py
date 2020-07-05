#!/usr/bin/env python3

""" ohd.py - (OverHead Door) is a complete re-write of my first completely useful Python utility.
My first project with a Raspberry Pi was intended to monitor a reed switch on my garage door,
and send me a text or email if it opened. That's not all it did, of course, but that's the gist.
It was finished in December of 2015, and ran flawlessly for three years.  The code was kludgy at best,
so I am re-writing it in an attempt to bring it more in line with good coding practices.  We shall see.
I am an amateur.  Learning as I go, I started on this in January, 2019.  Finished it on 01/26/19."""

import os
import sys
import configparser
import argparse
import logging
import time
import signal
import threading
import RPi.GPIO as GPIO
import socket
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
    logging.basicConfig(filename=ohdHome + '/ohd.log', format='%(asctime)s - %(message)s : %(name)s.', datefmt='%a, %d %b %Y %H:%M:%S', level=logging.INFO)
#
## End Command line arguments parsing

logger.info(" - - - - - - - - - - - - - - - - - - - - - - - - - - - - ")
logger.info("  INITIAL CONFIGURATION COMPLETE  ")
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
    logger.info(" NORMAL STARTUP AT THE TOP OF THE MAIN FUNCTION ")
    logger.info(" - - - - - - - - - - - - - - - - - - - - - - - - - - - - ")
    tt = 60
    bpFirst = 0
    openFirst = 0
    mdMsgSent = 0
    ohdsendmail.msgS("GarMon Status Change", "Garage Door Monitor started normally at ")
    pill2kill = threading.Event()
    pt = threading.Thread(target=getPins, args=(pill2kill,))
    pt.start()
    if "Thread-1" in str(threading.enumerate()):
        pcT = "running"
    else:
        pcT = "not running"
    logger.info("The getPins thread is " +  pcT)

    while True:
#
## ByPass Off and Door CLOSED is the normal state.  Nothing needs to be done.
#
#
## ByPass OFF and Door OPEN - - this is the ALARM STATE
#
        if bpStat == 'Off' and DoorStat == 'open' and openFirst == 0:   # First time: Notify Door is OPEN
            logger.info("ByPass is OFF and door is OPEN")
            openFirst = 1
            bpFirst = 0
            if Qtest != "Quiet":
                ohdsendmail.main()
            logger.debug("Starting the timer.")
            ttStart = time.time()                                              # Capture the time in ttStart


        elif bpStat == 'Off' and DoorStat == 'open' and openFirst == 1: # Subsequent times
            if time.time() - ttStart > tt and Qtest == "[]" and DoorStat == 'open':
                emAdd = config.get('CommandEmail', 'InBoundEmail1')
                Qtest, rmFrom, msgAuth = ohdreadmail.main()                     # Check for a Quiet message
                logger.info("ohdreadmail.main() returned Auth= " +msgAuth + "; "  + Qtest + ", From: " + rmFrom)
                if Qtest != 'Quiet':
                   logger.info("A minute has gone by.  Restarting time monitoring. Qtest = " + Qtest + ". Door is " + DoorStat) 
                   ohdsendmail.main()
                   Qtest = "[]"
                ttStart = time.time()
            else:
                if Qtest == "Quiet" and msgAuth == "Yes" and QmsgRcvdSent == 0:
                    ohdsendmail.msgS("Message Received", "A Quiet instruction was received from " + rmFrom + " at ") # the module function being called adds the timestamp.
                    QmsgRcvdSent = 1
#
## Turning ByPass ON while the Door is OPEN -- Notify once only
#
        if bpStat == 'On' and DoorStat == 'open':
            if bpFirst == 0:
                logger.info("Door OPEN and ByPass ON" + ". bpFirst=" + str(bpFirst))
                ohdsendmail.main()
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
            ohdsendmail.main()
            logger.info("bpFirst set to " + str(bpFirst))
            if argsohd.debug:
                time.sleep(1)

#
## Turning ByPass OFF while the door is closed.
#
        elif bpStat == 'Off' and DoorStat == 'closed' and bpFirst == 1:
            logger.info("ByPass was turned OFF")
            ohdsendmail.main()
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
            ohdsendmail.main()
            if argsohd.debug:
                time.sleep(1)
            openFirst = 0
            bpFirst = 0
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
            if mdMsgSent == 0:
                logger.info("pirStat is: " + pirStat + ". Bypass is: " + bpStat + ".  mdMsgSent is: " + str(mdMsgSent) + ". Starting ZM.")
                ohdpinchk.bellRing()
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect(('192.168.1.22', 6802))
                sock.send(b'6|on|25|PIR_Tripped|PIR|PIR \n7|on|25|PIR_Tripped|PIR|PIR \n8|on|25|PIR_Tripped|PIR|PIR \n9|on|25|PIR_Tripped|PIR|PIR \n10|on|25|PIR_Tripped|PIR|PIR')
                smt = threading.Thread(target=ohdsendmail.msgS, args=("PIR", "The Front Porch motion detector was tripped "))
                smt.start()
                threadCount = threading.active_count()
                logger.debug("threading.active_count is: " + str(threadCount))
                received = str(sock.recv(1024), "utf-8")
                logger.info("Motion detector was triggered. Command sent to Zoneminder.")
                logger.debug("Received from sock: \n" + received)
                mdMsgSent = 1
                pirStat = 'normal'
                logger.debug("The mdMsgSent variable was set to " + str(mdMsgSent))
                mdt = threading.Timer(int(mdDelay), motionDet)
                mdt.start()
                logger.debug("Started a threading.Timer. When it ends, the motionDet function will run.")
            if mdMsgSent == 2:
                mdt = threading.Timer(int(mdDelay), motionDet)
                mdt.start()
                threadCount = threading.active_count()
                logger.debug("threading.active_count is: " + str(threadCount))
                mdMsgSent = 3
#
## When something stops all this from being True, then we fall off the planet.
## I probably need do some exception catching stuff here . . .
#
    else:
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
    logger.debug("Top of threaded motionDet. " + str(threading.currentThread()))
    if mdMsgSent == 3:
        mdMsgSent = 1
    if mdMsgSent == 2:
        mdMsgSent = 1
    if mdMsgSent == 1 and pirStat == 'normal' and bpStat == 'Off':
        logger.info("pirStat is: " + pirStat)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('192.168.1.22', 6802))
        sock.send(b'6|cancel|||| \n7|cancel|||| \n8|cancel|||| \n9|cancel|||| \n10|cancel||||')
        received = str(sock.recv(1024), "utf-8")
        logger.debug("Received from sock: \n" + received + "Also, mdMsgSent: " + str(mdMsgSent) + ", being set to 0.")
        mdMsgSent = 0
    else:
        logger.info("pirStat is: " + pirStat)
        logger.debug("mdMsgSent: " + str(mdMsgSent) + ", setting to 2.")
        mdMsgSent = 2
        pass
#
## getPins is the function that gets started as a thread to continuously check the status of our triggers.
## This keeps the main function freed up and looping quickly, which enhances responsiveness.
#
def getPins(stop_event):
    global DoorStat, bpStat, pirStat, pill2kill, Qtest, openFirst, bpFirst, tt

    while not stop_event.wait(1):
        DoorStat = ohdpinchk.pinChk()
        bpStat = ohdpinchk.bpChk()
        pirStat = ohdpinchk.pirChk()
    else:
        logger.info("getPins dropped out")
        pass

def SignalHandler(signal, frame):
        global pill2kill
        print("SignalHandler invoked")
        pill2kill.set()
        logger.info(" - - - - - - - - - - - - - - - - - - - - - ")
        logger.info("Cleaning up")
        GPIO.cleanup()
        logger.debug("Finished GPIO.cleanup() in SignalHandler")
        logger.info("Shutting down gracefully")
        ohdsendmail.msgS("ohd Status Change", "Shutdown Initiated")
        logger.debug("Sent 'Shutdown Now' message")
        logger.debug("Wrote to log in SignalHandler")
        logger.info("Finished SignalHandler")
#        logger.flush()
#        logger.close()
        sys.exit(0)



if __name__ == "__main__":
        global pill2kill
        import traceback
        try:
            signal.signal(signal.SIGINT, SignalHandler)  ## This one catches CTRL-C from the local keyboard
            signal.signal(signal.SIGTERM, SignalHandler) ## This one catches the Terminate signal from the system
            logger.info(" Top of try")
            while True:
                main()
            pass

            logger.info("Bottom of try")
#            logger.flush()
        except Exception:
            pill2kill.set()
            error = traceback.print_exc()
            logger.debug(error)
            logger.info("That's all folks.  Goodbye")
