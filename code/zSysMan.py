#!/usr/bin/env python3
##
## This routine runs as a service, and looks for either rebootItNow or restartSvc.
## If it finds either of them, it deletes it and then either restarts the service, or reboots the machine. 
##
#   zSysMan.py is the standard version. Supports reboot and service restart.
#   zSysManG.py is the version for Raspberry Pi with a REBOOT button, but without an LCD. 'G' is for GPIO.
#   zSysManGL.py is the version for a Pi with an LCD. 'G' is for GPIO, 'L' is for LCD.

#     Copyright (c) 2022 - Gregory Allen Sanders.

#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
# No Warranty of any kind is provided for this code.

import time,os,logging,configparser,argparse,traceback,signal,sys
from time import sleep

parserWPB = argparse.ArgumentParser()
group = parserWPB.add_mutually_exclusive_group()
group.add_argument('-d', '--debug', help="Turn on debugging output to log file.", action="store_true")
group.add_argument('-f', '--func', help="Call the specified function.", action="store_true")
zsmHome = os.getcwd()
logger = logging.getLogger(__name__)
#
confparse = configparser.ConfigParser()
confparse.read(zsmHome + '/out.conf')
#
argsWPB = parserWPB.parse_args()

if argsWPB.debug:
    logging.basicConfig(filename=zsmHome + '/zSysMan.log', format='[%(name)s]:%(levelname)s: %(message)s. - %(asctime)s', datefmt='%D %H:%M:%S', level=logging.DEBUG)
    logging.info("Debugging output enabled")
else:
    logging.basicConfig(filename=zsmHome + '/zSysMan.log', format='%(asctime)s - %(message)s', datefmt='%a, %d %b %Y %H:%M:%S', level=logging.INFO)
#
logger.info(" - - - - zSysMan.py DATA LOGGING STARTED - - - - ")
logger.info("  INITIAL CONFIGURATION COMPLETE  ")
logger.info("zsmHOME path is: " + zsmHome)

#
## - - - - - MAIN CODE BELOW HERE - - - -
#
def main():
    if os.path.isfile(zsmHome + '/rebootItNow'):
        os.remove(zsmHome + '/rebootItNow')
        if os.path.isfile(zsmHome + '/rebootItNow'):
            logger.info('Failed to remove reboot file.')
        else:
            logger.info('Found reboot file and deleted it.  Sending reboot command now.')
            os.system('reboot')
    if os.path.isfile(zsmHome + '/restartSvc'):
        with open(zsmHome + '/restartSvc', 'r') as res:
            whatSvc = res.readline()
        os.remove(zsmHome + '/restartSvc')
        if os.path.isfile(zsmHome + '/restartSvc'):
            logger.info('Failed to remove restartSvc file.')
        else:
            logger.info('Found restartSvc file and deleted it. Restarting {}'.format(whatSvc))
            os.system('systemctl restart ' + whatSvc)

    if os.path.isfile(zsmHome + '/stopSvc'):
        with open(zsmHome + '/stopSvc', 'r') as res:
            whatSvc = res.readline()
        os.remove(zsmHome + '/stopSvc')
        if os.path.isfile(zsmHome + '/stopSvc'):
            logger.info('Failed to remove stopSvc file.')
        else:
            logger.info('Found stopSvc file and deleted it. Stopping {}'.format(whatSvc))
            os.system('systemctl stop ' + whatSvc)

    sleep(2)
#
## - - - - - - END MAIN CODE - - - - - - - 
#

def SignalHandler(signal, frame):
    if signal == 2:
        sigStr = 'CTRL-C'
        logger.info('* * * ' + sigStr + ' caught. * * * ')
    print("SignalHandler invoked")
    logger.info("Shutting down gracefully")
    logger.debug("Wrote to log in SignalHandler")
    logger.info("That's all folks.  Goodbye")
    logger.info(" - - - - zSysMan.py DATA LOGGING STOPPED BY DESIGN - - - - ")
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, SignalHandler)  ## This one catches CTRL-C from the local keyboard
    signal.signal(signal.SIGTERM, SignalHandler) ## This one catches the Terminate signal from the system    
    try:
        print(" Top of try")
        while True:
            main()
#        main()
        pass
#                print("Bottom of try")
    except Exception:
        logger.info("Exception caught at bottom of try.", exc_info=True)
        error = traceback.print_exc()
        logger.info(error)
        logger.info("That's all folks.  Goodbye")
        logger.info(" - - - - ZSysMan.py DATA LOGGING STOPPED BY EXCEPTION - - - - ")