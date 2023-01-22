#!/usr/bin/env python3

# import time,os,logging,configparser,argparse,traceback,signal,sys,subprocess,io
import time,os,logging,argparse,traceback,signal,sys,subprocess,io,ohdSoftBP
from time import sleep

#
## - - - - - TEST CODE BELOW HERE - - - -
#
def main():
    # ohdSoftBP.blinkOn()
    # what = ohdSoftBP.SBPCheck()
    # print(what)
    # sleep(20)
    # ohdSoftBP.blinkOff()
    what = ohdSoftBP.SBPCheck()
    print(what)
    sys.exit(0)

# def main():
#     BlinkTestHome = os.getcwd()
#     blinkOn()
#     sleep(60)
#     blinkOff()
#     sys.exit(0)

# def blinkOn():
#     BlinkTestHome = os.getcwd()
#     pipeOut = open(BlinkTestHome + '/inpipe', 'wb')
#     start = str.encode('start')
#     pipeOut.write(start)
#     bOnReturn = 'Sent start.'
#     print(bOnReturn)
#     pipeOut.flush()
#     pipeOut.close()
#     return bOnReturn

# def blinkOff():
#     BlinkTestHome = os.getcwd()
#     pipeOut = open(BlinkTestHome + '/inpipe', 'wb')
#     stop = str.encode('stop')
#     pipeOut.write(stop)
#     bOffReturn = 'Sent stop.'
#     print(bOffReturn)
#     pipeOut.flush()
#     pipeOut.close()
#     return bOffReturn


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
    logger.info(" - - - - blinktest.py DATA LOGGING STOPPED INTENTIONALLY - - - - ")
    sys.exit(0)

if __name__ == "__main__":

    BlinkTestHome = os.getcwd()                              ## os.getcwd() give you the Current Working Directory.  If you run this from some other directory
    # print(BlinkTestHome)                                     ## then the blink.log file (for example) gets written there, not in the directory where this 
    logger = logging.getLogger(__name__)                ## python file lives. By using this BlinkTestHome variable before filenames, it insures a correct path to the files.  
    parserBlinkTest = argparse.ArgumentParser()
    parserBlinkTest.add_argument('-d', '--debug', help="Turn on debugging output to log file.", action="store_true")
    argsBlinkTest = parserBlinkTest.parse_args()
    if argsBlinkTest.debug:
        logging.basicConfig(filename=BlinkTestHome + '/blink.log', format='[%(name)s]:%(levelname)s: %(message)s. - %(asctime)s', datefmt='%D %H:%M:%S', level=logging.DEBUG)
        logging.info("Debugging output enabled")
    else:
        logging.basicConfig(filename=BlinkTestHome + '/blink.log', format='%(asctime)s - %(message)s', datefmt='%a, %d %b %Y %H:%M:%S', level=logging.INFO)
    #
    logger.info(" - - - - blinkTest.py DATA LOGGING STARTED - - - - ")
    # print('Logger info')
    #
    signal.signal(signal.SIGINT, SignalHandler)  ## This one catches CTRL-C from the local keyboard
    signal.signal(signal.SIGTERM, SignalHandler) ## This one catches the Terminate signal from the system    
    try:
#        print(" Top of try")
#        while True:  # use this 'while' loop to run main() over and over.
#            main()
#            pass
        main()        # using this outside the 'while' loop runs it only once.
    except Exception:
        logger.info("Exception caught at bottom of try.", exc_info=True)
        error = traceback.print_exc()
        logger.info(error)
        logger.info("That's all folks.  Goodbye")
        logger.info(" - - - - blinkTest.py DATA LOGGING STOPPED BY EXCEPTION - - - - ")