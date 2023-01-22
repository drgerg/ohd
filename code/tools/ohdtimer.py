#!/usr/bin/env python3

import time
import os
import logging



def timer(duration, dotNum, threadStop):
    logger = logging.getLogger(__name__)
    starttime = time.time()
    dur = duration
    logging.info("Variable 'duration' == " + str(duration) + "; Variable 'dur' == " + str(dur))
    logging.debug("Main() started with a parameter of : " + str(dur) + ", threadStop = " + str(threadStop))
    while time.time() - starttime < dur and threadStop == False:
        for i in range(dur):
            if dotNum == "N":
                print("\033[F" + str(dur-i) + "     " + str(threadStop))
            else:
                print("\033[F\033[K" + "." * (i+1) + str(threadStop))
            time.sleep(1)
    else:
        timerReturn = "done"
        threadStop = True
        logger.info("The timer returned: " + timerReturn + ". ThreadStop is " + str(threadStop))
        return timerReturn, threadStop

if __name__=="__main__":
    try:
        import argparse
        global threadStop
        threadStop = False
## Command line arguments parsing
#
        parsertmr = argparse.ArgumentParser()
        parsertmr.add_argument("-d", "--debug", help="Turn on debugging output to stderr", action="store_true")
        parsertmr.add_argument("-n", "--nums", help="Print countdown numbers rather than the progress dots.", action="store_true")
        parsertmr.add_argument("-s", "--seconds", type=int, metavar='N', default=0, help="How long (in seconds) this timer should run before exiting and returning 'done'.")
        parsertmr.add_argument("-dd", "--ddebug", help="Turn on Deep Debugging output to log file.", action="store_true")
        argstmr = parsertmr.parse_args()
        if argstmr.debug:
            logging.basicConfig(filename='/home/greg/ohd/timer.log', format='[%(name)s]:%(levelname)s: %(message)s. - %(asctime)s', datefmt='%D %H:%M:%S', level=logging.DEBUG)
            logging.info("ohdtimer.py started with debugging output enabled")
        else:
            logging.basicConfig(filename='/home/greg/ohd/timer.log', format='%(asctime)s - %(message)s in %(name)s.', datefmt='%a, %d %b %Y %H:%M:%S', level=logging.INFO)
        if argstmr.seconds:
            duration = argstmr.seconds
            print("ohdtimer.py started with a duration value of :" + str(duration) + "\n")
            logging.debug("End of config section.  duration == " + str(duration))
## End Command line arguments parsing
        if argstmr.nums:
            print(argstmr.nums)
            dotNum = "N"
        else:
            dotNum = None
        timer(duration, dotNum, threadStop)
    except:
        pass
                

