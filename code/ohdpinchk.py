#!/usr/bin/env python3

# ohdpinchk.py - (OverHead Door) Check and return the status of the specified GPIO pin.
#    2019,2020,2021 - Gregory Allen Sanders

import os,sys,logging,time,signal,ohdSoftBP
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
GPIO.setup(23, GPIO.OUT)
GPIO.setup(25, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)
logger.debug("All them little GPIOs are set up")
#
## End GPIO setup

def main():
    logger.debug("Started the Main() function")
    time.sleep(1)
    logger.info("The door is " + pinChk() + ". Bypass is " + bpChk() +". Motion is " + pirChk() + ". " + cpuTemp())
    logger.debug("Finished the Main() function")
    print(DoorStat)         # These print lines are used by Brilliant zTest.py to bring 
    print(bpStat)           # these values to Mother.
    print(cpuT)             # Don't comment them out thinking they are abandoned test lines.
    print(pirStat)
    return bpStat, DoorStat, cpuT

def pirChk():
    global pirStat
    if GPIO.input(27) == False:
        pirStat = 'normal'
    else:
        pirStat = 'triggered'
#    logger.debug("PIR: " + pirStat)
    return pirStat

def pinChk():
    global DoorStat
#    logger.debug("At top of pinChk()")
    if GPIO.input(24) == False:
        DoorStat = 'closed'
        GPIO.output(25, GPIO.LOW)
    else:
        DoorStat = 'open'
        GPIO.output(25, GPIO.HIGH)
#    logger.debug("Door: " + DoorStat)
    return DoorStat

def bpChk(bpStatv):
    global bpStat
    bpStat = bpStatv
    justOn = 0
    # logger.info("At top of bpChk()")
    SBPStat = ohdSoftBP.SBPCheck()
    # logger.info('bpStat: ' + bpStat + ', SBPStat: ' + SBPStat)
#
    if SBPStat == 'start':                                    ## Soft Bypass status START. Established by ohdSoftBP.blinkOn()
        bpStat = 'On'

    if SBPStat == 'stop':                                     ## Soft Bypass status STOP. Established by ohdSoftBP.blinkOff()
        bpStat = 'Off'

    if SBPStat == 'stop' and GPIO.input(12) == False:         ## Button pushed in (ByPass is On). This reports as False.
        bpStat = 'On'
        GPIO.output(21, GPIO.HIGH)

    if SBPStat == 'stop' and GPIO.input(12) == True:          ## Button popped out (ByPass is Off). This reports as True.
        GPIO.output(21, GPIO.LOW)
        bpStat = 'Off'

    if SBPStat == 'override' and GPIO.input(12) == False:
        GPIO.output(21, GPIO.LOW)
        ohdSoftBP.override()                                  ## Sets SBPStat to 'stop' and turns off blinking LED
        bpStat = 'Off'
    return bpStat

def bellRing():
    # logger.info("Ringing the doorbell.")
    GPIO.output(23, GPIO.HIGH)
    time.sleep(.1)
    GPIO.output(23, GPIO.LOW)
    time.sleep(.5)
    GPIO.output(23, GPIO.HIGH)
    time.sleep(.1)
    GPIO.output(23, GPIO.LOW)
    time.sleep(.5)
    GPIO.output(23, GPIO.HIGH)
    time.sleep(.1)
    GPIO.output(23, GPIO.LOW)
    rangBell = "Rang the Doorbell."
    return rangBell

#
## Grab the CPU temperature while you're at it.
#
def cpuTemp():
    global cpuT
# Return CPU temperature as a character string
    ct = os.popen('vcgencmd measure_temp').readline()
    cpuRtn = ct.replace("temp=","").replace("'C\n","")
    temp1=float(cpuRtn)
    temp2= '{:.2f}'.format(float(9/5 * temp1 + 32.00))
    cpuT = "CPU: " + str(temp1) + "C" + " (" + str(temp2) + "F)"
    return cpuT

def SignalHandler(signal, frame):
        logger.info(" = = = = = = = = = = = = = = Cleaning up = = = = = = = = = = = = = = = = = = ")
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
        parserpc.add_argument('-f', '--func', help="Call the specified function.", action="store")
        argspc = parserpc.parse_args()
        ohdHome = os.getcwd()
        if argspc.debug:
            logging.basicConfig(filename=ohdHome + '/ohd.log', format='[%(name)s]:%(levelname)s: %(message)s. - %(asctime)s', datefmt='%D %H:%M:%S', level=logging.DEBUG)
            logging.info("Debugging output enabled")
        else:
            logging.basicConfig(filename=ohdHome + '/ohd.log', format='%(asctime)s - %(message)s.', datefmt='%a, %d %b %Y %H:%M:%S', level=logging.INFO)
        #
        ## End Command line arguments parsing

        signal.signal(signal.SIGINT, SignalHandler)
        logger.debug("Top of try")
        if argspc.func:
            Pfunc = str(argspc.func + '()')
            print(Pfunc)
            Pfunc
        else:
            import ohdSoftBP
            bpChk()
        # print(bpStat)
        logger.info("Bottom of try in ohdPinChk.py")

    except:
        pass
        logger.info("That's all folks.  Goodbye from ohdPinChk.py")

