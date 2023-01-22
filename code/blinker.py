#!/usr/bin/env python3

# import time,os,logging,configparser,argparse,traceback,signal,sys,subprocess,io
import time,os,logging,argparse,traceback,signal,sys,threading
import RPi.GPIO as GPIO
from time import sleep
#
## - - - - - TEST CODE BELOW HERE - - - -
#
def main():
    # logger.info('blinker.py started.')
    # global PInStr
    # PInStr = 'stop'
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(21, GPIO.OUT)
    BlinkerHome = os.getcwd()
    # pipeT = threading.Thread(target=getPipe, name='fifoT')  # This points to a Linux named pipe by the name of 'inpipe'. See below.
    # pipeT.start()
    # print('Started fifoT: ' + str(threading.enumerate()) + '\n')  # fifoT should show up.
    pipeIn = open('inpipe', 'rb', 0)                           # 'inpipe' is a 'Linux named pipe'.  It's created by the 'mkfifo' command.
    PInStr = bytes.decode(pipeIn.readline())
    # logger.info('inpipe from blinker.py PInStr: ' + PInStr)
    while PInStr != 'stop':
        if PInStr == 'start':
            while PInStr != 'stop':
                # logger.info('PInStr: ' + PInStr)
                GPIO.output(21, GPIO.HIGH)
                time.sleep(.5)
                GPIO.output(21, GPIO.LOW)
                time.sleep(.5)
                PInStr = bytes.decode(pipeIn.readline())
                # logger.info('Toggled GPIO.output(21). Re-read pipeIn: ' + str(PInStr))
        if PInStr == 'override':
            while PInStr != 'stop':
                GPIO.output(21, GPIO.HIGH)
                time.sleep(.2)
                GPIO.output(21, GPIO.LOW)
                time.sleep(.2)
                PInStr = bytes.decode(pipeIn.readline())
                # logger.info('Toggled GPIO.output(21). Re-read pipeIn: ' + str(PInStr))
    if PInStr == 'stop':
        GPIO.output(21, GPIO.LOW)
            
    # else:
    #     logger.info('PInStr: ' + PInStr)
        # GPIO.output(21, GPIO.LOW)
        


def getPipeT():
    global PInStr
    # while True:
    pipeIn = open('inpipe', 'rb', 0)                           # 'inpipe' is a 'Linux named pipe'.  It's created by the 'mkfifo' command.
    PInStr = bytes.decode(pipeIn.readline())


def getPipe():
    pipeIn = open('inpipe', 'rb', 0)                           # 'inpipe' is a 'Linux named pipe'.  It's created by the 'mkfifo' command.
    PInStr = bytes.decode(pipeIn.readline())
    # logger.info('Threaded function getPipe() stopped.')
    return PInStr

def getPInStr():
    global PInStr
    return PInStr


#
#
#  REMEMBER: The writing process blocks until the pipe is read.
#
#


## - - - - - - END TEST CODE - - - - - - - 
#














def SignalHandler(signal, frame):
    if signal == 2:
        sigStr = 'CTRL-C'
        logger.info('* * * ' + sigStr + ' caught. * * * ')
    print("SignalHandler invoked")
    logger.info("Shutting down gracefully")
    logger.debug("Wrote to log in SignalHandler")
    logger.info("That's all folks.  Goodbye")
    logger.info(" - - - - blinker.py DATA LOGGING STOPPED INTENTIONALLY - - - - ")
    sys.exit(0)

if __name__ == "__main__":


    BlinkerHome = os.getcwd()                              ## os.getcwd() give you the Current Working Directory.  If you run this from some other directory
    # print(BlinkerHome)                                     ## then the blink.log file (for example) gets written there, not in the directory where this 
    logger = logging.getLogger(__name__)                ## python file lives. By using this BlinkerHome variable before filenames, it insures a correct path to the files.  
    parserBlinker = argparse.ArgumentParser()
    parserBlinker.add_argument('-d', '--debug', help="Turn on debugging output to log file.", action="store_true")
    argsBlinker = parserBlinker.parse_args()
    if argsBlinker.debug:
        logging.basicConfig(filename=BlinkerHome + '/ohd.log', format='[%(name)s]:%(levelname)s: %(message)s. - %(asctime)s', datefmt='%D %H:%M:%S', level=logging.DEBUG)
        logging.info("Debugging output enabled")
    else:
        logging.basicConfig(filename=BlinkerHome + '/ohd.log', format='%(asctime)s - %(message)s', datefmt='%a, %d %b %Y %H:%M:%S', level=logging.INFO)
    #
    logger.info(" - - - - blinker.py DATA LOGGING STARTED - - - - ")
    # print('Logger info')
    #
    signal.signal(signal.SIGINT, SignalHandler)  ## This one catches CTRL-C from the local keyboard
    signal.signal(signal.SIGTERM, SignalHandler) ## This one catches the Terminate signal from the system    
    try:
#        print(" Top of try")
       while True:  # use this 'while' loop to run main() over and over.
           main()
           pass
        # print("Starting ohdBlinker.service.\n")
        # main()        # using this outside the 'while' loop runs it only once.}
    except Exception:
        logger.info("Exception caught at bottom of try.", exc_info=True)
        error = traceback.print_exc()
        logger.info(error)
        logger.info("That's all folks.  Goodbye")
        logger.info(" - - - - blinker.py DATA LOGGING STOPPED BY EXCEPTION - - - - ")